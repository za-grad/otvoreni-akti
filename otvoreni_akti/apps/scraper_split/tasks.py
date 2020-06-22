from celery import shared_task
from .scrape import start


@shared_task
def celery_scrape_everything():
    start()
    return 'All new acts scraped'
