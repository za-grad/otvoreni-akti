from django.test import TestCase
import pytest
from ..models import ScraperPeriod
from .. import scrape_utils_dates

pytestmark = pytest.mark.django_db

root_url = 'http://web.zagreb.hr'
test_url_2017 = '/sjednice/2017/Sjednice_2017.nsf/web_pretraga?OpenForm&BaseTarget=desni'
test_url_2009 = '/sjednice/Sjednice_2009.nsf/web_pretraga?OpenForm&BaseTarget=desni'


class TestExtractMonths(TestCase):
    """This test uses requires City Website to be online and reachable."""
    def test_function_extracts_correct_months(self):
        month_list_2018 = scrape_utils_dates.extract_months('2018', root_url + test_url_2017)
        month_list_2020 = scrape_utils_dates.extract_months('2020', root_url + test_url_2017)
        self.assertIn('5. studenog 2018. - 9.studenog 2018', month_list_2018)
        self.assertIn('20. siječnja 2020. - 24.siječnja 2020', month_list_2020)


class TestExtractDates(TestCase):
    """This test uses requires City Website to be online and reachable."""
    def test_function_extracts_correct_dates(self):
        self.assertEqual(ScraperPeriod.objects.count(), 0)
        scrape_utils_dates.extract_dates('2017-20xx', test_url_2017)
        self.assertGreater(ScraperPeriod.objects.count(), 0)
        target_period = ScraperPeriod.objects.get(period_text='6. kolovoza 2019. - 9.kolovoza 2019')
        self.assertEqual(target_period.year_range, '2017-20xx')

    def test_function_ignores_duplicate_data(self):
        self.assertEqual(ScraperPeriod.objects.count(), 0)
        scrape_utils_dates.extract_dates('2009-2013', test_url_2009)
        period_count = ScraperPeriod.objects.count()

        # Try to add duplicate period data
        scrape_utils_dates.extract_dates('2009-2013', test_url_2009)
        self.assertEqual(ScraperPeriod.objects.count(), period_count)
