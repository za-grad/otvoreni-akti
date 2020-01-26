import pickle

from scrape_utils import scrape_everything

# Increased recursion limit to prevent 'maximum recursion depth exceeded' error
import sys
sys.setrecursionlimit(3000)

with open('skupstina.pkl', 'wb') as f:
    subjects = scrape_everything()
    pickle.dump(subjects, f)
