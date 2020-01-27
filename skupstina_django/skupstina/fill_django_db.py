import pickle
import os
from .models import Category, Source, Item, Act


def find_pickles(scraper_path):
    pickles = []
    for file in os.listdir(scraper_path):
        if file.endswith('.pkl'):
            pickles.append(os.path.join(scraper_path, file))
    return pickles


def fill_django_db():
    # Populate the Category table
    for type_description in ['akti_gradonacelnika',
                             'dnevni_red_skupstine',
                             'pitanja_odgovori',
                             'dnevni_red_radna_tijela']:
        if not Category.objects.filter(type=type_description).exists():
            new_type = Category(type=type_description)
            new_type.save()

    found_pickles = find_pickles('../skupstina_scraper/')

    if found_pickles:
        for found_pickle in found_pickles:
            with open(found_pickle, 'rb') as f:
                subjects = pickle.load(f)
                print('Opened pickle file...')
                for subject in subjects:
                    for act in subject['details']['acts']:
                        # Populate the Act table
                        content = act['act_text']
                        if not Act.objects.filter(content_url=act['act_url']).exists():
                            print('Adding ', act['act_title'])
                            new_act = Act(
                                subject=act['act_title'],
                                content=content,
                                content_url=act['act_url'],
                                type=''
                            )
                            new_act.save()
            print('Added items from ', found_pickle)
    else:
        print('No new data found.')


fill_django_db()
