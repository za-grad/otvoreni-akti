import re
from datetime import datetime
from django.utils import timezone
import dateparser
from bs4 import BeautifulSoup

from .models import ScraperPeriod
from otvoreni_akti.apps.search.models import Period, Item, Subject, Act
from otvoreni_akti.apps.common_utils.scrape_utils_docu import extract_pdffile_data
from otvoreni_akti.apps.common_utils.scrape_utils_requests import requests_retry_session
from otvoreni_akti.settings import ACTS_ROOT_URL_RIJEKA as root_url


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


def scrape_new_sessions(dummy='dummy'):
    """
    Searches for any new new sessions on the Grad Rijeka website and adds them to the database.
    Note: The dummy input is required for requests_patcher (mock requests) to work.
    """

    print('Searching for any new sessions to be scraped from Grad Rijeka database...')
    current_session_urls = set(ScraperPeriod.objects.values_list('url', flat=True))

    page_url = root_url + '/gradska-uprava/gradonacelnik/gradonacelnikov-kolegij/page/'
    next_page = 1
    found_cnt = 0

    while next_page:
        full_url = f'{page_url}{next_page}/'
        print(f'Parsing session page {full_url}')
        site = requests_retry_session().get(full_url).content
        soup = BeautifulSoup(site, 'html.parser')

        sessions = soup.select('div.component-content > article > header')

        next_page += 1

        for session in sessions:
            raw_date = session.small.get_text(strip=True)
            url = session.h3.a['href']
            title = session.h3.a.get_text(strip=True)
            info = re.sub(' gradona.elnik(ov|a)', '', title)
            date = text_to_date(raw_date)

            if url in current_session_urls:
                print(f'Found already processed url {url}, skipping...')
            else:
                print(f"Found new session: {info} - {date.strftime('%d %b %Y')}...")
                found_cnt += 1
                ScraperPeriod.objects.create(
                    url=url,
                    date=date,
                    period_text=f"{info[:84]} - {date.strftime('%d.%b.%Y')}"
                )

        if soup.select('div.component-pagination > ul.page-numbers') == []:
            print('Pagination bar not found, no more pages to scrape')
            next_page = None

    print(f'Found {found_cnt} new sessions')


def scrape_session(scraper_period):
    site = requests_retry_session().get(scraper_period.url).content
    soup = BeautifulSoup(site, 'html.parser')

    print(f'Scraping new session from Grad Rijeka for {scraper_period.period_text} from {scraper_period.url}')

    if not Period.objects.filter(period_url=scraper_period.url).exists():
        period = Period.objects.create(
            period_text=scraper_period.period_text,
            start_date=scraper_period.date,
            end_date=scraper_period.date,
            period_url=scraper_period.url,
        )
    else:
        period = Period.objects.get(period_url=scraper_period.url)

    sections = soup.select('div.main-content > div.component > ol > li')

    for item_no, section in enumerate(sections, start=1):
        print(f'Scraping item {item_no}  from Grad Rijeka for {scraper_period.period_text}')
        item_title = f'#{item_no} - {period}'
        if not Item.objects.filter(item_title=item_title).exists():
            item = Item.objects.create(
                period=period,
                item_title=item_title,
                item_number=item_no,
                item_text='Blank',
            )
        else:
            item = Item.objects.get(item_title=item_title)

        documents = section.select('div.item-documents > ul > li')

        for document in documents:
            full_url = document.a['href']
            title = document.a.get_text(strip=True)

            # create Subject object
            if not Subject.objects.filter(subject_url=full_url).exists():
                subject = Subject.objects.create(
                    item=item,
                    subject_title=title,
                    subject_url=full_url,
                )
            else:
                subject = Subject.objects.get(subject_url=full_url)

            print(f"Scraping new act from Grad Rijeka for {title} from {full_url}")
            pdf_text = extract_pdffile_data(url_pdf=full_url)

            # create Act object
            if not Act.objects.filter(content_url=full_url).exists():
                Act.objects.create(
                    subject=subject,
                    title=title,
                    content_url=full_url,
                    content=pdf_text,
                    file_type='pdf',
                    city='Rijeka',
                )

    scraper_period.scrape_completed = True
    scraper_period.save()


def scrape_new_acts(*args, **kwargs):
    """
    Initial scrape to scrape all open acts with an option to scrape last n dates.
    :param kwargs:
        int max_periods:
            Scrapes the latest acts within the last 'max_periods' periods.
    """
    if 'max_periods' in kwargs:
        max_periods = kwargs['max_periods']
        sessions_to_scrape = ScraperPeriod.objects.filter(scrape_completed=False).order_by('-date')[:max_periods]
    else:
        sessions_to_scrape = ScraperPeriod.objects.filter(scrape_completed=False).order_by('-date')

    if sessions_to_scrape:
        for scraper_period in sessions_to_scrape:
            scrape_session(scraper_period)
