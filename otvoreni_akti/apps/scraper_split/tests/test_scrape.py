import os
from datetime import datetime
from django.utils import timezone
import pytest

from .. import scrape_utils, scrape
from ..scrape_utils import text_to_date, scrape_new_acts
from ..models import ScraperPeriod
from otvoreni_akti.apps.common_utils.tests.mock_requests import requests_patcher
from otvoreni_akti.apps.search.models import Period, Item, Subject, Act

pytestmark = pytest.mark.django_db
file_path = os.path.dirname(os.path.abspath(__file__))


class TestTextToDate:
    def test_function_returns_correct_date_from_normal_string(self):
        date_string = '02. Studeni 2016'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2016, 11, 2, 0, 0))

    def test_function_returns_correct_date_from_strange_string(self):
        date_string = '12_Studeni_2016__'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2016, 11, 12, 0, 0))

        date_string = '02_Studeni_2016 (1)'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2016, 11, 2, 0, 0))

        date_string = '03_Studeni_2016(1)'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2016, 11, 3, 0, 0))

        date_string = '04_Studeni_2016_SOME_STUFF'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2016, 11, 4, 0, 0))

        date_string = "05_Studeni_201'6"
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2016, 11, 5, 0, 0))

    def test_function_returns_correct_date_for_studenoga(self):
        date_string = '02_Studenoga_2016__'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2016, 11, 2, 0, 0))

    def test_function_returns_correct_date_for_studenog(self):
        date_string = '02_studenog_2016__'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2016, 11, 2, 0, 0))

    def test_function_returns_correct_date_for_sijecnj(self):
        date_string = '02_Sijecnj_2016__'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2016, 1, 2, 0, 0))

    def test_function_returns_correct_date_for_lipnj(self):
        date_string = '02-lipnj_2016-'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2016, 6, 2, 0, 0))


class TestScrapeNewPeriods:
    def test_function_extracts_correct_data(self):
        with open(file_path + '/dummy_website/dummy_split_site.html', 'rb') as file:
            requests_patcher(
                parent_module=scrape_utils,
                function_to_patch=scrape_utils.scrape_new_periods,
                payload=file.read()
            )
            assert ScraperPeriod.objects.count() == 2328


class TestScrape:
    """This test uses requires Grad Split website to be online and reachable."""
    def test_function_scrapes_correct_data(self):
        scrape.start(max_periods=2)
        assert ScraperPeriod.objects.count() > 0
        assert Period.objects.count() == 2
        assert Item.objects.count() == 2
        assert Subject.objects.count() == 2
        assert Act.objects.count() == 2

        # Manually set scraped periods to incomplete to trigger rescrape
        for scraper_period in ScraperPeriod.objects.all():
            scraper_period.scrape_completed = False
            scraper_period.save()

        scrape_new_acts(max_periods=2)
        assert Period.objects.count() == 2
        assert Item.objects.count() == 2
        assert Subject.objects.count() == 2
        assert Act.objects.count() == 2
