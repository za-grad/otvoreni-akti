from django.test import TestCase
from mixer.backend.django import mixer
import pytest

pytestmark = pytest.mark.django_db


class TestSearchHome(TestCase):
    def test_home_view_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'search/search_home.html')


class TestSearchResults(TestCase):
    def setUp(self) -> None:
        period1 = mixer.blend('search.Period')
        period2 = mixer.blend('search.Period')

    def test_results_view_uses_correct_template(self):
        response = self.client.get('/search/?q=dubrovnik')
        self.assertTemplateUsed(response, 'search/search_results.html')

    def test_view_redirects_to_home_if_404(self):
        response = self.client.get('/gobbledeegook/')
        self.assertRedirects(response, '/')

    def test_results_view_redirects_to_home_if_no_get_request(self):
        response = self.client.get('/search/')
        self.assertRedirects(response, '/')

    def test_results_view_uses_correct_template_if_no_query_string(self):
        response = self.client.get('/search/?start_date=')
        self.assertTemplateUsed(response, 'search/search_results.html')

    def test_can_handle_different_searches(self):
        # Search for 'Zagreb' may take a long time but shouldn't crash
        response = self.client.get('/search/?q=zagreb')
        self.assertEqual(response.status_code, 200)

        # Tests for keyword searches with odd combinations
        response = self.client.get('/search/?totallynotarealvariable=***()')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/search/?q=%26%26notnotandand')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/search/?q=zagrebandandnotnotordubrovnik')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/search/?q=zagreb and and not not or dubrovnik')
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

    def test_view_shows_correct_number_of_results(self):
        for i in range(100):
            mixer.blend('search.Act', content='Letsgetschwifti')
        period1 = mixer.blend('search.Period')
        period2 = mixer.blend('search.Period')
        response = self.client.get('/search/?q=Letsgetschwifti')
        self.assertTemplateUsed(response, 'search/search_results.html')
        self.assertNotContains(response, '20 results')
        self.assertContains(response, '100 results')


class TestActDetail(TestCase):
    def test_act_detail_view_uses_correct_template(self):
        mixer.blend('search.Act', content='Letsgetschwifti', id=1)
        response = self.client.get('/acts/1/')
        self.assertTemplateUsed(response, 'search/act_detail.html')
        self.assertContains(response, 'Letsgetschwifti')

