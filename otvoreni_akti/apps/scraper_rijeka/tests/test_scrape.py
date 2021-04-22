import os
from datetime import datetime
from django.utils import timezone
import pytest

from .. import scrape_utils, scrape
from ..scrape_utils import text_to_date, scrape_new_acts, scrape_session
from ..models import ScraperPeriod
from otvoreni_akti.apps.common_utils.tests.mock_requests import requests_patcher
from otvoreni_akti.apps.search.models import Period, Item, Subject, Act

pytestmark = pytest.mark.django_db
file_path = os.path.dirname(os.path.abspath(__file__))

class TestTextToDate:
    def test_function_returns_correct_date_from_expected_string(self):
        date_string = 'Utorak, 23. ozujak 2021.'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2021, 3, 23, 0, 0))

        date_string = '23. ozujak 2021.'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2021, 3, 23, 0, 0))

        date_string = '23. ozujka 2021.'
        date = text_to_date(date_string)
        assert date == timezone.make_aware(datetime(2021, 3, 23, 0, 0))


class TestScrapeNewPeriods:
    def test_function_extracts_sessions(self):
        with open(file_path + '/dummy_website/sessions_list_page.html', 'rb') as file:
            requests_patcher(
                parent_module=scrape_utils,
                function_to_patch=scrape_utils.scrape_new_sessions,
                payload=file.read()
            )
            assert ScraperPeriod.objects.count() == 2


class TestScrape:
    """This test uses requires Grad Rijeka website to be online and reachable."""
    def test_function_scrapes_correct_data(self):
        scrape.start(max_periods=2)
        assert ScraperPeriod.objects.count() > 0
        assert Period.objects.count() == 2
        assert Item.objects.count() > 2
        assert Subject.objects.count() > 2
        assert Act.objects.count() == Subject.objects.count()

        # Manually set scraped periods to incomplete to trigger rescrape
        for scraper_period in ScraperPeriod.objects.all():
            scraper_period.scrape_completed = False
            scraper_period.save()

        scrape_new_acts(max_periods=2)
        assert Period.objects.count() == 2
        assert Item.objects.count() > 2
        assert Subject.objects.count() > 2
        assert Act.objects.count() == Subject.objects.count()

    """This test uses requires Grad Rijeka website to be online and reachable."""
    def test_function_scrape_session(self):
        scraper_period = ScraperPeriod.objects.create(
            url='https://www.rijeka.hr/mayor-session/70-gradonacelnikov-kolegij-3/',
            date=datetime(2020, 11, 20, 0, 0),
            period_text='70. kolegij - Petak, 20. studeni 2020.'
        )

        scrape_session(scraper_period)
        assert Period.objects.count() == 1
        assert Item.objects.count() == 6
        assert Subject.objects.count() == 65
        assert Act.objects.count() == Subject.objects.count()
