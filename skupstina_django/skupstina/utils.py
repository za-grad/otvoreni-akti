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

    if 'and' in tokens:
        q = Q("multi_match", query=tokens[0], fields=['content', 'subject'])
        for token in tokens:
            if token != 'and':
                q = q & Q("multi_match", query=token, fields=['content', 'subject'])
    else:
        q = Q("multi_match", query=search_term, fields=['content', 'subject'])

    query_set = ActDocument.search().query(q)

    # Override Elasticsearch's default max of 10 results
    results = query_set[0:query_set.count()].execute()

    return results
