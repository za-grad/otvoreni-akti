from celery import shared_task

from otvoreni_akti.settings import RESCRAPE_LAST_N_PERIODS
from .scrape import start, rescrape


@shared_task
def celery_scrape_everything():
    start()
    return 'All new acts scraped'


@shared_task
def celery_rescrape_last_n(rescrape_last_n=RESCRAPE_LAST_N_PERIODS):
    rescrape(rescrape_last_n)
    return f'Rescraped last {rescrape_last_n} periods'
