"""Scrapes the last n items from scrapes_completed file."""
from .scrape_utils_data import scrape_last

# Scrapes last n entries in scrapes_completed file
n = 3
scrape_last(n, '/sjednice/2017/Sjednice_2017.nsf/DRJ?OpenAgent&')
