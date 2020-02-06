"""Scrape everything from the City database."""

from .scrape_utils_html import scrape_everything
from .scrape_utils_dates import extract_dates

# Dictionary linking each City database to its unique URL
akti_dict = {
    '2017-20xx': '/sjednice/2017/Sjednice_2017.nsf/DRJ?OpenAgent&',
    '2013-2017': '/sjednice/2013/Sjednice_2013.nsf/DRJ?OpenAgent&',
    '2009-2013': '/sjednice/Sjednice_2009.nsf/DRJ?OpenAgent&',
}

# Dictionary linking each City database to its sidebar URL
sidebar_dict = {
    '2017-20xx': '/sjednice/2017/Sjednice_2017.nsf/web_pretraga?OpenForm&BaseTarget=desni',
    '2013-2017': '/sjednice/2013/Sjednice_2013.nsf/web_pretraga?OpenForm&BaseTarget=desni',
    '2009-2013': '/sjednice/Sjednice_2009.nsf/web_pretraga?OpenForm&BaseTarget=desni',
}


def start(*args, **kwargs):
    """
    :param kwargs:
        int max_periods:
            Scrapes the latest acts within the last 'max_periods' periods.
            If max_periods is not defined or 0, it scrapes everything.
    """
    for k, v in sidebar_dict.items():
        print('Searching for any new date ranges to be scraped from {}...'.format(k))
        extract_dates(year_range=k, url_suffix=v)

    for k, v in akti_dict.items():
        print('Scrape started for date ranges in {}'.format(k))
        if 'max_periods' in kwargs:
            max_periods = kwargs['max_periods']
            scrape_everything(year_range=k, url_suffix=v, max_periods=max_periods)
        else:
            scrape_everything(year_range=k, url_suffix=v)


def rescrape():
    scrape_everything(
        rescrape_last_n=2,
        year_range='2017-20xx',
        url_suffix='/sjednice/2017/Sjednice_2017.nsf/DRJ?OpenAgent&',
    )
