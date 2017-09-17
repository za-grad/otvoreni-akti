from peewee import *
from skupstina.schema import db, Category, Source, Item, Act

# test = Act(subject='bla', content='blabla', content_url = 'http://web.zagreb.hr/sjednice/2013/Sjednice_2013.nsf/DRJ?OpenAgent&31.%20listopada%202016.%20-%204.studenog%202016')
# test.save()

# test2 = Act(subject='bla2', content='blabla2', content_url = 'http://web.zagreb.hr/sjednice/2013/Sjednice_2013.nsf/DRJ?OpenAgent&31.%20listopada%202016.%20-%204.studenog%202016')
# test2.save()


# for cat in Category.select():
#     print(cat.type, cat.created_ts)

# for act in Act.select():
#     print(act.subject, act.content, act.content_url)
#
try:
    db.create_tables([Category, Source, Item, Act])
except (ProgrammingError, OperationalError) as e:
    db.rollback()

for type_description in ['akti_gradonacelnika', 'dnevni_red_skupstine', 'pitanja_odgovori', 'dnevni_red_radna_tijela']:
    try:
        new_type = Category(type=type_description)
        new_type.save()
    except IntegrityError:
        db.rollback()

import pickle

with open('./skupstina.pkl', 'rb') as f:
    subjects = pickle.load(f)
    for subject in subjects:
        for act in subject['details']['acts']:
            # print(len(act['title']), len(act['text']), len(act['url']))
            try:
                content = act['text']
                # content = content.replace('\xB2', '2')
                # print(content)
                new_act = Act(subject=act['title'], content=content, content_url=act['url'], type='')
                new_act.save()
                print('wrote')
            except IntegrityError as e:
                print(e)
                db.rollback()
                continue
