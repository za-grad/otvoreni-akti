import re
from datetime import datetime
from django.utils import timezone
import dateparser
from bs4 import BeautifulSoup

from .models import ScraperPeriod
from otvoreni_akti.apps.search.models import Period, Item, Subject, Act
from otvoreni_akti.apps.common_utils.scrape_utils_docu import extract_pdffile_data
from otvoreni_akti.apps.common_utils.scrape_utils_requests import requests_retry_session
from otvoreni_akti.settings import ACTS_ROOT_URL_SPLIT as root_url


def text_to_date(raw_date: str) -> datetime:
    """Converts raw dates in Croatian to datetime after cleaning them."""
    raw_date = raw_date.lower()
    date_string_1 = re.sub('[\'\"\.]','', raw_date)
    date_string_2 = re.sub('studenoga|studenog','studeni', date_string_1)
    date_string_3 = re.sub('sijecnj[ \-\_]','sijecnja', date_string_2)
    date_string_4 = re.sub('lipnj[ \-\_]','lipnja', date_string_3)
    date_string_final = re.search('.*\d{4}', date_string_4).group(0)

    # parse date and make timezone aware
    date = dateparser.parse(date_string_final, languages=['hr'])
    date = timezone.make_aware(date)
    return date


def scrape_new_periods(dummy='dummy'):
    """
    Searches for any new new periods on the Grad Split website and adds them to the database.
    Note: The dummy input is required for requests_patcher (mock requests) to work.
    """
    print('Searching for any new date ranges to be scraped from Grad Split database...')
    full_url = root_url + '/gradska-uprava/gradonacelnik/akti-gradonacelnika'
    site = requests_retry_session().get(full_url).content
    soup = BeautifulSoup(site, 'html.parser')
    raw_urls = soup.select('.c-documents-list__item-link')

    # Create dictionary of links:titles
    raw_urls_dict = {
        url['href']:                                               # dict key of hrefs
        text_to_date(url.div.get_text(strip=True))                 # dict value of titles in datetime format
        for url in raw_urls
    }
    raw_urls_set = {k for k in raw_urls_dict}

    existing_urls = set(ScraperPeriod.objects.values_list('url', flat=True))
    new_urls = raw_urls_set.difference(existing_urls)

    # create new ScraperPeriod objects if required
    if new_urls:
        for url in new_urls:
            date = raw_urls_dict[url]

            # fix bug for date in 2107
            if date.strftime('%Y') == '2107':
                date = date.replace(year=2017)

            print(f"Found new period: {date.strftime('%d %b %Y')}...")
            ScraperPeriod.objects.create(
                url=url,
                date=date,
                date_text=date.strftime('%d.%b.%Y')
            )


def scrape_new_acts(*args, **kwargs):
    """
    Initial scrape to scrape all open acts with an option to scrape last n dates.
    :param kwargs:
        int max_periods:
            Scrapes the latest acts within the last 'max_periods' periods.
    """
    if 'max_periods' in kwargs:
        max_periods = kwargs['max_periods']
        periods_to_scrape = ScraperPeriod.objects.filter(scrape_completed=False).order_by('-date')[:max_periods]
    else:
        periods_to_scrape = ScraperPeriod.objects.filter(scrape_completed=False).order_by('-date')

    if periods_to_scrape:
        for scraper_period in periods_to_scrape:
            full_url = root_url + scraper_period.url

            print(f"Scraping new act from Grad Split for {scraper_period.date_text} from {scraper_period.url}")
            pdf_text = extract_pdffile_data(url_pdf=full_url)

            # create Period object
            period_text = f'{scraper_period.date_text} to {scraper_period.date_text}'
            if not Period.objects.filter(period_text=period_text).exists():
                period = Period.objects.create(
                    period_text=period_text,
                    start_date=scraper_period.date,
                    end_date=scraper_period.date,
                    period_url=full_url,
                )
            else:
                period = Period.objects.get(period_text=period_text)

            # create Item object
            item_title = f'#1 from period {period}'
            if not Item.objects.filter(item_title=item_title).exists():
                item = Item.objects.create(
                    period=period,
                    item_title=item_title,
                    item_number=1,
                    item_text='Blank',
                )
            else:
                item = Item.objects.get(item_title=item_title)

            # create Subject object
            if not Subject.objects.filter(subject_url=full_url).exists():
                subject = Subject.objects.create(
                    item=item,
                    subject_title=f'Split akti {scraper_period.date_text}',
                    subject_url=full_url,
                )
            else:
                subject = Subject.objects.get(subject_url=full_url)

            # create Act object
            if not Act.objects.filter(content_url=scraper_period.url).exists():
                Act.objects.create(
                    subject=subject,
                    title=f'Split akti {scraper_period.date_text}',
                    content_url=scraper_period.url,
                    content=pdf_text,
                    file_type='pdf',
                    city='Split',
                )

            scraper_period.scrape_completed = True
            scraper_period.save()
