"""Scrape everything from the City database."""

from otvoreni_akti.settings import RESCRAPE_LAST_N_PERIODS
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
    This function first checks if there are any new periods that have been added to the Grad Zagreb website
    since the last performed scrape. It only scrapes new periods that are not inside the ScraperPeriod model
    and does not check for new acts added to a previously scraped period in the ScraperPeriod model.

    Example:
    1. The last full scrape was done on 29.Feb.2020.
    2. The database has all acts from 28.Feb.2020 to 03.June.2009
    3. This function is run on 08.Mar.2020.
    4. If it finds that a new period has been added (03.Mar.2020 to 08.Mar.2020), it will scrape all the acts from
       this new period.
    5. If it finds that no new periods have been added since 28.Feb.2020, it will exit.

    :param kwargs:
        int max_periods:
            Scrapes the latest acts within the last 'max_periods' periods.
            If max_periods is not defined or 0, it scrapes everything.
    """
    for k, v in sidebar_dict.items():
        print('Searching in Grad Zagreb for any new date ranges to be scraped from {}...'.format(k))
        extract_dates(year_range=k, url_suffix=v)

    for k, v in akti_dict.items():
        print('Scrape of Grad Zagreb started for date ranges in {}'.format(k))
        if 'max_periods' in kwargs:
            max_periods = kwargs['max_periods']
            scrape_everything(year_range=k, url_suffix=v, max_periods=max_periods)
        else:
            scrape_everything(year_range=k, url_suffix=v)


def rescrape(rescrape_last_n: int = RESCRAPE_LAST_N_PERIODS):
    """
    This function rescrapes the last rescrape_last_n periods inside the ScraperPeriod model. It only
    saves new acts that were added to previously scraped periods in the ScraperPeriod model.
    It does not check for new periods added to the Grad Zagreb website since the last scrape.start().

    Example:
    1. The last full scrape was done on 29.Feb.2020.
    2. The database has all acts from 28.Feb.2020 to 03.June.2009
    3. This function is run on 08.Mar.2020 with rescrape_last_n = 2.
    4. If a new period has been added (03.Mar.2020 to 08.Mar.2020) to Grad Zagreb, it will ignore this new period.
    5. This function will check for new acts within the last 2 scraped periods,
       i.e. 24.Feb.2020 to 28.Feb.2020 and 17.Feb.2020 to 21.Feb.2020.
    6. If new acts are found within these 2 previously scraped periods, it will save them.

    :param
        int rescrape_last_n:
            Rescrapes the latest acts within the last 'rescrape_last_n' periods.
            Example: rescrape_last_n=10 will rescrape the last 10 scraped periods of acts once again.
    """
    scrape_everything(
        rescrape_last_n=rescrape_last_n,
        year_range='2017-20xx',
        url_suffix='/sjednice/2017/Sjednice_2017.nsf/DRJ?OpenAgent&',
    )
