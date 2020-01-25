import pickle
from .models import Category, Source, Item, Act


def fill_django_db():
    # Populate the Category table
    for type_description in ['akti_gradonacelnika',
                             'dnevni_red_skupstine',
                             'pitanja_odgovori',
                             'dnevni_red_radna_tijela']:
        if not Category.objects.filter(type=type_description).exists():
            new_type = Category(type=type_description)
            new_type.save()

    with open('../skupstina.pkl', 'rb') as f:
        subjects = pickle.load(f)
        for subject in subjects:
            for act in subject['details']['acts']:
                # Populate the Act table
                content = act['text']
                if not Act.objects.filter(content_url=act['url']).exists():
                    new_act = Act(subject=act['title'], content=content, content_url=act['url'], type='')
                    new_act.save()

        print('wrote')


fill_django_db()
