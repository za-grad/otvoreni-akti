from bs4 import BeautifulSoup
from .scrape_utils_requests import requests_retry_session


def extract_months(year, url):
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


def extract_dates(period, url):
    with open('scraper/data/akti_' + period + '.txt', 'r+', encoding='utf8') as periods_fd:
        months_on_file = periods_fd.read().splitlines()
        site = requests_retry_session().get(url).content
        soup = BeautifulSoup(site, 'html.parser')
        years_soup = soup.find("select", {'name': 'rb_godina'}).findAll('option')
        # Get list of years in descending order
        year_list = years_soup[0].text.split('\n')
        year_list.sort(reverse=True)
        for year in year_list:
            month_list = extract_months(year, url)
            for month in month_list:
                if month not in months_on_file:
                    print('Adding {} to {}'.format(month, periods_fd))
                    periods_fd.write('{}\n'.format(month))

