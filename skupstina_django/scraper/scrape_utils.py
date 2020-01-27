import re
import requests
from bs4 import BeautifulSoup
from skupstina.models import Category, Source, Item, Act

root_url = 'http://web.zagreb.hr'


def parse_subjects_list(url):
    site = requests.get(url).content
    soup = BeautifulSoup(site, 'html.parser')
    els = soup.select('.centralTD ul ol li')
    print(len(els), ' elements')
    subjects = []
    for el in els:
        subel = el.contents[0]
        print(subel)
        try:
            link = subel.attrs['href']
        except AttributeError:
            continue
        title = subel.select('b')[0].contents[0]
        subjects.append({'title:': title, 'subject_url': root_url + link})
    return subjects, len(els)


def get_visible_text(soup):
    # Additional check for pages with JavaScript redirects
    if 'location.replace(' in soup.getText():
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


def parse_subject_details(url):
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
        act_text = get_visible_text(soup)
        act_title = act_titles[i]
        acts.append({'act_text': act_text, 'act_url': act_url, 'act_title': act_title})
    subject_details['acts'] = acts
    return subject_details


def scrape_everything(url_suffix: str, akti_file: str):
    all_subjects = []
    periods_url = root_url + url_suffix
    with open('scrapes_completed.txt', 'a', encoding='utf8') as f:
        # Create a new file if not already created
        pass
    with open('scraper/data/' + akti_file, encoding='utf8') as periods_fd:
        for act_period in list(periods_fd)[:3]:         # To release the Kraken, remove the [:2] >;D
            with open('scrapes_completed.txt', 'r+', encoding='utf8') as scrapes_completed:
                if act_period not in scrapes_completed.read():
                    parse_complete = False
                    act_period = act_period.strip()
                    print('\nScraping period: ', act_period)
                    url = (periods_url + act_period).replace(' ', '%20')
                    print(url)
                    subjects, num_els = parse_subjects_list(url)
                    all_subjects.extend(subjects)
                    while not parse_complete:
                        for subject in subjects:
                            if 'details' not in subject:
                                try:
                                    print('Parsing ', subject['subject_url'])
                                    subject_details = parse_subject_details(subject['subject_url'])
                                    subject['details'] = subject_details
                                    for act in subject['details']['acts']:
                                        # Populate the Act table
                                        content = act['act_text']
                                        if not Act.objects.filter(content_url=act['act_url']).exists():
                                            print('Adding ', act['act_title'])
                                            new_act = Act(
                                                subject=act['act_title'],
                                                content=content,
                                                content_url=act['act_url'],
                                                type=''
                                            )
                                            new_act.save()
                                    print('Parsed  ', subject['subject_url'], ' **')
                                    parse_complete = True
                                except:
                                    print('Error occurred in parsing ', subject['subject_url'])
                                    parse_complete = False
                    scrapes_completed.write('{}\n'.format(act_period))
    print(all_subjects)


# def item_checker():
#     act_url = '/sjednice/2017/Sjednice_2017.nsf/Dokument_opci_sjednica_noatt_web?OpenForm&ParentUNID=6591FDDD6E4FEF15C12584F00030C87E'
#     # act_url = '/sjednice/2017/Sjednice_2017.nsf/Dokument_opci_sjednica_noatt_web?OpenForm&ParentUNID=6591FDDD6E4FEF15C12584F00030C87E&AutoFramed'
#     site = requests.get(root_url + act_url).content
#     print(root_url + act_url, '\n')
#     soup = BeautifulSoup(site, 'html.parser')
#     act_text = get_visible_text(soup)
#     print('Act text:', act_text)
# item_checker()
