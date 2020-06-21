from datetime import datetime
from django.test import TestCase
from elasticsearch_dsl.response import Response
from .. import utils


class TestElasticSearch(TestCase):
    default_start_date = str(datetime(1900, 1, 1, 0, 0))
    default_end_date = str(datetime.now())

    def test_function_handles_normal_search_requests(self):
        results = utils.elastic_search(
            search_term='Seemingly normal search term',
            start_date=self.default_start_date,
            end_date=self.default_end_date,
            sort_by='relevance',
            file_type='All',
            city='All',
        )
        self.assertEqual(type(results), Response)

    def test_function_handles_search_requests_in_quotations(self):
        results = utils.elastic_search(
            search_term='"Quotations"',
            start_date=self.default_start_date,
            end_date=self.default_end_date,
            sort_by='relevance',
            file_type='All',
            city='Zagreb',
        )
        self.assertEqual(type(results), Response)

    def test_function_handles_wrong_dates(self):
        results = utils.elastic_search(
            search_term='Normal',
            start_date='some garbage date',
            end_date='another garbage date',
            sort_by='newest_first',
            file_type='All',
            city='All',
        )
        self.assertEqual(type(results), Response)

    def test_function_handles_all_operators_and_quotations(self):
        results = utils.elastic_search(
            search_term='and "This test" contains operators and funny or "awesome symbols" not uncommon',
            start_date=self.default_start_date,
            end_date=self.default_end_date,
            sort_by='oldest_first',
            file_type='html',
            city='All',
        )
        self.assertEqual(type(results), Response)

    def test_function_handles_consecutive_operators(self):
        results = utils.elastic_search(
            search_term='and or not and and or or not not andnotor not and or or and and and',
            start_date=self.default_start_date,
            end_date=self.default_end_date,
            sort_by='relevance',
            file_type='All',
            city='All',
        )
        self.assertEqual(type(results), Response)

    def test_function_handles_single_operator_only(self):
        results = utils.elastic_search(
            search_term='or',
            start_date=self.default_start_date,
            end_date=self.default_end_date,
            sort_by='relevance',
            file_type='All',
            city='All',
        )
        self.assertEqual(type(results), Response)

    def test_function_handles_empty_string(self):
        results = utils.elastic_search(
            search_term='',
            start_date=self.default_start_date,
            end_date=self.default_end_date,
            sort_by='relevance',
            file_type='All',
            city='All',
        )
        self.assertEqual(type(results), Response)
