import dateparser
import re
from datetime import datetime, timedelta
from django.utils import timezone
from elasticsearch_dsl import Q

from otvoreni_akti.settings import MAX_SEARCH_RESULTS
from .documents import ActDocument, act_analyzer


def elastic_search(search_term, *args, **kwargs):
    """
    Search function using Elasticsearch.

    :param str search_term:
        Search term input by user
        Accepts the following keywords inside search_term:
        'AND' : Use AND before search terms that must be included
        'NOT' : Use NOT before search terms that must be excluded
        'OR' : Use OR or space between search terms to include all terms
        "" : Search terms inside quotation marks will be searched for an exact match

    :param kwargs:
        datetime start_date: Excludes any results before start_date
        datetime end_date: Excludes any results after end_date

    :return: query_set results:
        Returns search results to view
    """
    # Regex to search for exact terms within quotation marks
    exact_search_terms = re.findall(r'"(.*?)"', search_term)
    exact_terms_dict = {}
    if exact_search_terms:
        for i, exact_term in enumerate(exact_search_terms):
            if exact_term:
                exact_terms_dict['ex__' + str(i)] = exact_term
                search_term = search_term.replace(exact_term, 'ex__' + str(i))

    # Break the search term into individual tokens
    response = act_analyzer.simulate(search_term)
    tokens = [t.token for t in response.tokens]
    print(tokens)

    # Parse start and end dates (stores None if these are invalid)
    start_date = dateparser.parse(kwargs['start_date'])
    end_date = dateparser.parse(kwargs['end_date'])

    # Check for garbage user inputs for dates and add padding if valid
    if start_date:
        start_date = timezone.make_aware(start_date) - timedelta(hours=12)

    if end_date:
        end_date = timezone.make_aware(end_date) + timedelta(hours=12)

    keywords = {'and', 'not', 'or'}
    query_string = ''

    # Create a string to be evaluated later
    for position, token in enumerate(tokens):
        if token in keywords and (position == 0 or position == len(tokens)-1):
            # Ignore any keywords if they are the first or last search term
            pass
        elif token in exact_terms_dict:
            query_string += """Q('query_string', query='"{}"', fields=['content', 'title']) |"""\
                .format(exact_terms_dict[token])
        elif token == 'and':
            query_string = query_string[:-1] + "&"
        elif token == 'or':
            query_string = query_string[:-1] + "|"
        elif token == 'not':
            query_string = query_string[:-1] + "& ~"
        else:
            query_string += "Q('multi_match', query='{}', fields=['content', 'title']) |".format(token)

    if query_string:
        if query_string[-1] == '&' or query_string[-1] == '|':
            # Pop the last character
            query_string = query_string[:-1]
        print(query_string)
        try:
            q = eval(query_string)
        except SyntaxError as e:
            print('Syntax error occurred in evaluating query:\n', e)
            q = Q('multi_match', query='', fields=['content', 'title'])
    else:
        # In case of no user input
        q = Q('multi_match', query='', fields=['content', 'title'])

    query_set = ActDocument.search()\
        .query(q)\
        .highlight('content', fragment_size=50) \
        .filter(
        'range',
        **{'subject__item__period__end_date': {'from': start_date, 'to': timezone.now()}}
    )\
        .filter(
        'range',
        **{'subject__item__period__start_date': {'from': datetime(1900, 1, 1, 0, 0), 'to': end_date}}
    )\
        .params(request_timeout=30)

    # Override Elasticsearch's default max of 10 results
    results = query_set[0:MAX_SEARCH_RESULTS].execute()
    return results
