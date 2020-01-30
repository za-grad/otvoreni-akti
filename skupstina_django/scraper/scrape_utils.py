import re
import time
import requests
from requests import exceptions
from bs4 import BeautifulSoup
from .db_utils import write_period_to_db, write_subject_to_db, write_act_to_db

root_url = 'http://web.zagreb.hr'


def get_visible_text(soup) -> str:
    # Additional check for pages with JavaScript redirects
    if 'location.replace(' in soup.getText():
        # Regex to extract redirect URL from the 'else' branch of Javascript code
        result = re.search('else\n {4}location.replace[(]"(.*)"[)];', soup.getText())
        act_url = result.group(1)
        site = requests.get(root_url + act_url).content
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
    site = requests.get(url).content
    soup = BeautifulSoup(site, 'html.parser')
    table_items = soup.select('.centralTD ul ol li')
    print(len(table_items), ' elements')
    subjects = []
    for table_item in table_items:
        content = table_item.contents[0]
        try:
            link = content.attrs['href']
        except AttributeError:
            continue
        subject_title = content.select('b')[0].contents[0]
        subjects.append({'subject_title': subject_title, 'subject_url': root_url + link})
    return subjects, len(table_items)


def parse_subject_details(url: str) -> dict:
    site = requests.get(url).content
    soup = BeautifulSoup(site, 'html.parser')

    text = get_visible_text(soup)
    subject_details = {'text': text}

    act_titles = [el.get_text().strip() for el in soup.select('td a')]
    act_urls = [el.attrs['href'] for el in soup.select('td a')]

    acts = []
    for i, act_url in enumerate(act_urls):
        site = requests.get(root_url + act_url).content
        soup = BeautifulSoup(site, 'html.parser')
        act_content = get_visible_text(soup)
        act_title = act_titles[i]
        acts.append({'act_content': act_content, 'act_url': act_url, 'act_title': act_title})
    subject_details['acts'] = acts
    return subject_details


def scrape_everything(url_suffix: str, akti_file: str):
    periods_url = root_url + url_suffix
    with open('scrapes_completed.txt', 'a', encoding='utf8') as f:
        # Create a new file if not already created
        pass
    with open('scraper/data/' + akti_file, encoding='utf8') as periods_fd:
        for act_period in list(periods_fd)[:2]:
            with open('scrapes_completed.txt', 'r+', encoding='utf8') as scrapes_completed:
                if act_period not in scrapes_completed.read():
                    act_period = act_period.strip()
                    print('\nScraping period: ', act_period)
                    url = (periods_url + act_period).replace(' ', '%20')
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
                    scrapes_completed.write('{}\n'.format(act_period))
