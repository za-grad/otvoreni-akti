from django.test import TestCase
from mixer.backend.django import mixer
import pytest

pytestmark = pytest.mark.django_db


class TestSearchHome(TestCase):
    def test_home_view_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'search/search_home.html')


class TestSearchResults(TestCase):
    def test_results_view_uses_correct_template(self):
        period1 = mixer.blend('search.Period')
        period2 = mixer.blend('search.Period')
        response = self.client.get('/search/?q=dubrovnik')
        self.assertTemplateUsed(response, 'search/search_results.html')

    def test_can_handle_different_searches(self):
        period1 = mixer.blend('search.Period')
        period2 = mixer.blend('search.Period')

        # Search for 'Zagreb' may take a long time but shouldn't crash above 10,000 results
        response = self.client.get('/search/?q=zagreb')
        self.assertEqual(response.status_code, 200)

        # Tests for keyword searches with odd combinations
        response = self.client.get('/search/?q=%26%26notnotandand')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/search/?q=zagrebandandnotnotordubrovnik')
        self.assertEqual(response.status_code, 200)

        # Tests for incorrect dates
        response = self.client.get(
            '/search/?q="imenovanju+%C4%8Dlana" not %C5%A0kolskog and predla%C5%BEe'
            '&start_date=2019-10-32'
            '&end_date=2099-02-30'
        )
        self.assertEqual(response.status_code, 200)

        # Tests for empty search
        response = self.client.get('/search/?q=')
        self.assertEqual(response.status_code, 200)
