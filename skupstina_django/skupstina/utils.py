import dateparser
from datetime import datetime, timedelta
from elasticsearch_dsl import Q
from .documents import ActDocument, act_analyzer

base_url = 'http://web.zagreb.hr/'


def elastic_search(search_term, *args, **kwargs):
    response = act_analyzer.simulate(search_term)
    tokens = [t.token for t in response.tokens]
    print(tokens)

    # Parse start and end dates into strings
    start_date = dateparser.parse(kwargs['start_date'])
    end_date = dateparser.parse(kwargs['end_date'])

    keywords = {'and', 'not'}
    keywords_in_tokens = len(keywords.intersection(set(tokens))) > 0
    if keywords_in_tokens:
        q = Q("multi_match", query=tokens[0], fields=['content', 'title'])
        for keyword_position, token in enumerate(tokens):
            if token in keywords:
                if keyword_position + 1 != len(tokens):
                    new_query = Q("multi_match", query=tokens[keyword_position+1], fields=['content', 'title'])
                    if token == 'and':
                        q = q & new_query
                    elif token == 'not':
                        q = q & ~new_query
    else:
        q = Q("multi_match", query=search_term, fields=['content', 'title'])

    query_set = ActDocument.search()\
        .query(q)\
        .highlight('content', fragment_size=50) \
        .filter(
        'range',
        **{'subject__item__period__end_date': {'from': start_date - timedelta(1), 'to': datetime.now()}}
    )\
        .filter(
        'range',
        **{'subject__item__period__start_date': {'from': datetime(1900, 1, 1, 0, 0), 'to': end_date}}
    )

    # Override Elasticsearch's default max of 10 results
    results = query_set[0:10000].execute()
    return results
