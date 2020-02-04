from bs4 import BeautifulSoup
from .models import ScraperPeriod
from .db_utils import parse_date_range
from .scrape_utils_requests import requests_retry_session
from otvoreni_akti.settings import ACTS_ROOT_URL as root_url


def extract_months(year: str, url: str) -> list:
    payload = {
        '__Click': '$Refresh',
        'SaveOptions': 0,
        'server': 'szglotweb',
        'trazi': '',
        '% % Surrogate_rb_godina': 1,
        'rb_godina': year,
        '% % Surrogate_rb_sjednice': 1,
    }
    site = requests_retry_session().post(url, data=payload).content
    soup = BeautifulSoup(site, 'html.parser')
    months_soup = soup.find("select", {'name': 'rb_sjednice'}).findAll('option')
    month_list = months_soup[0].text.split('\n')
    # Remove any empty items from month_list
    month_list = list(filter(None, month_list))
    return month_list


def extract_dates(year_range: str, url_suffix: str) -> None:
    url = root_url + url_suffix
    months_on_file = list(ScraperPeriod.objects.all().values_list('period_text', flat=True))
    site = requests_retry_session().get(url).content
    soup = BeautifulSoup(site, 'html.parser')
    years_soup = soup.find("select", {'name': 'rb_godina'}).findAll('option')
    year_list = years_soup[0].text.split('\n')
    for year in year_list:
        month_list = extract_months(year, url)
        for month in month_list:
            if month not in months_on_file:
                start_date, end_date = parse_date_range(month)
                print('Adding {} to {}'.format(month, year_range))
                ScraperPeriod.objects.create(
                    period_text=month,
                    year_range=year_range,
                    start_date=start_date,
                    end_date=end_date,
                )
