import pickle

from skupstina import scrape_everything

with open('skupstina.pkl', 'wb') as f:
    subjects = scrape_everything()
    pickle.dump(subjects, f)
