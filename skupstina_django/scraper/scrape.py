from .scrape_utils_html import scrape_everything
from .scrape_utils_dates import extract_dates

# Dictionary linking each akti_*.txt file to its unique URL
akti_dict = {
    'akti_2017-20xx.txt': '/sjednice/2017/Sjednice_2017.nsf/DRJ?OpenAgent&',
    'akti_2013-2017.txt': '/sjednice/2013/Sjednice_2013.nsf/DRJ?OpenAgent&',
    'akti_2009-2013.txt': '/sjednice/Sjednice_2009.nsf/DRJ?OpenAgent&',
}

# Dictionary linking each Act database to its sidebar URL
sidebar_dict = {
    '2017-20xx': 'http://web.zagreb.hr/sjednice/2017/Sjednice_2017.nsf/web_pretraga?OpenForm&BaseTarget=desni',
    '2013-2017': 'http://web.zagreb.hr/sjednice/2013/Sjednice_2013.nsf/web_pretraga?OpenForm&BaseTarget=desni',
    '2009-2013': 'http://web.zagreb.hr/sjednice/Sjednice_2009.nsf/web_pretraga?OpenForm&BaseTarget=desni',
}


for k, v in sidebar_dict.items():
    print('Searching for any new date ranges to be scraped from {}...'.format(k))
    extract_dates(period=k, url=v)


for k, v in akti_dict.items():
    print('Scrape started for date ranges in {}'.format(k))
    scrape_everything(akti_file=k, url_suffix=v)
