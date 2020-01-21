from django.db.models import Q
from .documents import ActDocument, act_analyzer
from .models import Act

base_url = 'http://web.zagreb.hr/'


def sql_search(search_term):
    query_set = Act.objects.filter(
        Q(content__icontains=search_term)
        | Q(subject__icontains=search_term)
    ).distinct()
    result = {'matches': [base_url + m.content_url for m in query_set]}
    return result


def elastic_search(search_term):
    query_set = ActDocument.search().filter("match", content=search_term)
    result = {'matches': [base_url + m.content_url for m in query_set]}

    # Check the token used for searching
    # response = act_analyzer.simulate(search_term)
    # tokens = [t.token for t in response.tokens]
    # print(tokens)

    return result
