from django.db.models import Q as QDjango
from elasticsearch_dsl import Q
from .documents import ActDocument, act_analyzer
from .models import Act

base_url = 'http://web.zagreb.hr/'


def sql_search(search_term):
    """Returns result in JSON format"""
    query_set = Act.objects.filter(
        QDjango(content__icontains=search_term)
        | QDjango(subject__icontains=search_term)
    ).distinct()
    results = {'matches': [base_url + m.content_url for m in query_set]}
    return results


def elastic_search(search_term):
    response = act_analyzer.simulate(search_term)
    tokens = [t.token for t in response.tokens]
    print(tokens)

    keywords = {'and', 'not'}
    keywords_in_tokens = len(keywords.intersection(set(tokens))) > 0
    if keywords_in_tokens:
        q = Q("multi_match", query=tokens[0], fields=['content', 'subject'])
        for keyword_position, token in enumerate(tokens):
            if token in keywords:
                if keyword_position + 1 != len(tokens):
                    new_query = Q("multi_match", query=tokens[keyword_position+1], fields=['content', 'subject'])
                    if token == 'and':
                        q = q & new_query
                    elif token == 'not':
                        q = q & ~new_query
    else:
        q = Q("multi_match", query=search_term, fields=['content', 'subject'])

    query_set = ActDocument.search()\
        .query(q)\
        .highlight('content', fragment_size=50)

    # Override Elasticsearch's default max of 10 results
    results = query_set[0:10000].execute()
    return results
