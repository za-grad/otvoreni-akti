from django.test import TestCase
from mixer.backend.django import mixer
import pytest
pytestmark = pytest.mark.django_db


class TestScraperPeriod(TestCase):
    def test_model(self):
        obj = mixer.blend('scraper_rijeka.ScraperPeriod')
        self.assertEqual(obj.pk, 1)

    def test_str(self):
        obj = mixer.blend('scraper_rijeka.ScraperPeriod')
        self.assertEqual(str(obj), obj.url)
