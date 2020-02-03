import re
import time
from requests import exceptions
from bs4 import BeautifulSoup
from .models import ScraperPeriod
from .db_utils import write_period_to_db, write_subject_to_db, write_act_to_db
from .scrape_utils_requests import requests_retry_session
from .scrape_utils_docu import parse_document_link
from skupstina_django.settings import ACTS_ROOT_URL as root_url


def get_visible_text(soup) -> str:
    # Additional check for pages with JavaScript redirects
    if 'location.replace(' in soup.getText():
        # Regex to extract redirect URL from the 'else' branch of Javascript code
        result = re.search('else\n {4}location.replace[(]"(.*)"[)];', soup.getText())
        act_url = result.group(1)
        site = requests_retry_session().get(root_url + act_url).content
        soup = BeautifulSoup(site, 'html.parser')
        text = get_visible_text(soup)
        return text
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
    text = soup.getText()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text


def parse_subjects_list(url: str) -> tuple:
    site = requests_retry_session().get(url).content
    soup = BeautifulSoup(site, 'html.parser')
    table_items = soup.select('.centralTD ul ol li')
    print(len(table_items), ' elements')
    subjects = []
    for table_item in table_items:
        content = table_item.contents[0]
        try:
            link = content.attrs['href'].lower()
        except AttributeError:
            continue
        subject_title = content.select('b')[0].contents[0]
        subjects.append({'subject_title': subject_title, 'subject_url': root_url + link})
    return subjects, len(table_items)


def parse_subject_details(url: str) -> dict:
    site = requests_retry_session().get(url).content
    soup = BeautifulSoup(site, 'html.parser')

    text = get_visible_text(soup)
    subject_details = {'text': text}

    act_titles = [el.get_text().strip() for el in soup.select('td a')]
    act_urls = [el.attrs['href'].lower() for el in soup.select('td a')]

    acts = []
    for i, act_url in enumerate(act_urls):
        site = requests_retry_session().get(root_url + act_url).content
        soup = BeautifulSoup(site, 'html.parser')
        act_content = get_visible_text(soup)
        act_title = act_titles[i]
        acts.append(
            {
                'act_content': act_content,
                'act_url': act_url,
                'act_title': act_title,
                'act_file_type': 'HTML',
            }
        )

    # Check for word or pdf attachments
    if "<a href='" in text:
        # Regex to extract link to document
        docu_urls = re.findall("<a href='(.*)','Dokument", text)
        for docu_url in docu_urls:
            docu_title, docu_raw_data, docu_file_type = parse_document_link(docu_url)
            acts.append(
                {
                    'act_content': docu_raw_data,
                    'act_url': docu_url,
                    'act_title': docu_title,
                    'act_file_type': docu_file_type,
                }
            )
    subject_details['acts'] = acts
    return subject_details


def scrape_engine(act_period: str, periods_url: str) -> None:
    """
    Scraper engine used to scrape open act.

    :param str act_period:
        Example: '20. siječnja 2020. - 24.siječnja 2020'

    :param str periods_url:
        Example: 'http://web.zagreb.hr/sjednice/2017/Sjednice_2017.nsf/DRJ?OpenAgent&'
    """
    act_period = act_period.strip().lower()
    print('\nScraping period: ', act_period)
    url = (periods_url + act_period).replace(' ', '%20').lower()
    print(url)
    period_obj = write_period_to_db(act_period, url)
    subjects, num_els = parse_subjects_list(url)
    for subject in subjects:
        parse_complete = False
        max_retries = 10
        sleep_time = 10
        print('Parsing ', subject['subject_url'])
        while not parse_complete and max_retries > 0:
            try:
                subject_details = parse_subject_details(subject['subject_url'])
                parse_complete = True
            except exceptions.ConnectionError as e:
                parse_complete = False
                max_retries -= 1
                print('Connection Error while parsing {}:\n{}\n'.format(subject['subject_url'], e))
                print('Retrying...\n')
                time.sleep(sleep_time)
        if max_retries == 0:
            print('Maximum retries exceeded. Please run the scraper again.\n')
            raise exceptions.ConnectionError
        subject['details'] = subject_details
        subject_obj = write_subject_to_db(subject, period_obj)
        write_act_to_db(subject['details']['acts'], subject_obj)
        print('Parsed  ', subject['subject_url'], ' **')


def scrape_everything(year_range: str, url_suffix: str, *args, **kwargs) -> None:
    """
    Initial scrape to scrape all open acts with an option to scrape last n dates.

    :param str url_suffix:
        URL suffix for which range of years to scrape.

    :param str year_range:
        Range of years to scrape from.
        Example: '2017-20xx'

    :param kwargs:
        int scrape_last_n: Scrapes only the last 'scrape_last_n' acts in 'year_range'
    """
    periods_url = root_url + url_suffix.lower()
    count = 0
    for scraper_period in ScraperPeriod.objects.all().order_by('-start_date'):
        if 'scrape_last_n' in kwargs:
            if scraper_period.scrape_completed is True \
                    and scraper_period.year_range == year_range\
                    and count < kwargs['scrape_last_n']:
                scrape_engine(scraper_period.period_text, periods_url)
                count += 1
        elif scraper_period.scrape_completed is False and scraper_period.year_range == year_range:
            scrape_engine(scraper_period.period_text, periods_url)
            scraper_period.scrape_completed = True
            scraper_period.save()
