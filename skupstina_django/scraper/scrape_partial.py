"""
Scrape all the acts once again from the last n date ranges from the City database.
This is useful for checking any new Acts that were added since our last scrape.
"""
from .scrape_utils_html import scrape_everything

scrape_everything(
    scrape_last_n=2,
    year_range='2017-20xx',
    url_suffix='/sjednice/2017/Sjednice_2017.nsf/DRJ?OpenAgent&',
)
