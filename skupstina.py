
# coding: utf-8

# In[1]:

import requests
from bs4 import BeautifulSoup


# Parse a list of subjects

# In[124]:

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
        #print(title)
        #print(link)
        subjects.append({'title:': title, 'subject_url': root_url + link})
    return subjects

#subjects = parse_subjects_list('http://web.zagreb.hr/sjednice/Sjednice_2009.nsf/DRJ?OpenAgent&3.%20lipnja%202013.%20-%207.lipnja%202013')
#subjects = parse_subjects_list('http://web.zagreb.hr/sjednice/2013/Sjednice_2013.nsf/DRJ?OpenAgent&5.%20lipnja%202017.%20-%209.lipnja%202017')
# subjects = parse_subjects_list('http://web.zagreb.hr/sjednice/2013/Sjednice_2013.nsf/DRJ?OpenAgent&31.%20listopada%202016.%20-%204.studenog%202016')
# print(subjects)


# Parse all acts for a subject

# In[118]:

def get_visible_text(soup):
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
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

    #print(text)

    act_titles = [el.get_text().strip() for el in soup.select('td a')]
    act_urls = [el.attrs['href'] for el in soup.select('td a')]

    acts = []
    for i, act_url in enumerate(act_urls):
        site = requests.get(root_url + act_url).content
        soup = BeautifulSoup(site, 'html.parser')
        act_text = get_visible_text(soup)
        act_title = act_titles[i]
        acts.append({'text': act_text, 'url': act_url, 'title': act_title})
    subject_details['acts'] = acts
    return subject_details

# subject = parse_subject_details('http://web.zagreb.hr/Sjednice/Sjednice_2009.nsf/PW?OpenForm&ParentUNID=38EF85D771DCDD7DC1257B7C002EA9F8TARGET="_top"')
# print(subject)


# # Connect everything

# In[119]:

def scrape_everything():
    all_subjects = []
    periods_url = root_url + '/sjednice/2013/Sjednice_2013.nsf/DRJ?OpenAgent&'
    with open('./data/akti.txt') as periods_fd:
        for act_period in list(periods_fd)[:1]:
            act_period = act_period.strip()
            print('scraping period: ', act_period)
            url = (periods_url + act_period).replace(' ', '%20')
            print(url)
            subjects = parse_subjects_list(url)
            all_subjects.extend(subjects)
            for subject in subjects:
                subject_details = parse_subject_details(subject['subject_url'])
                subject['details'] = subject_details
    return all_subjects

#all_subjects = scrape_everything()
#print(all_subjects)


# In[ ]:
