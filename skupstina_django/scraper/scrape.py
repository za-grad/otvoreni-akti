from .scrape_utils import scrape_everything

# Dictionary linking each akti_*.txt file to its unique URL
akti_dict = {
    'akti_2017-20xx.txt': '/sjednice/2017/Sjednice_2017.nsf/DRJ?OpenAgent&',
    'akti_2013-2017.txt': '/sjednice/2013/Sjednice_2013.nsf/DRJ?OpenAgent&',
    'akti_2009-2013.txt': '/sjednice/Sjednice_2009.nsf/DRJ?OpenAgent&',
}

for k, v in akti_dict.items():
    subjects = scrape_everything(akti_file=k, url_suffix=v)
