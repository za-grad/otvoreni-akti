from skupstina.schema import db, Act

from playhouse.postgres_ext import Match

base_url = 'http://web.zagreb.hr/'

def search(query):
    matches = Act.select().where(Act.content.contains(query))
    # TODO: use this to rely on Postgres' full-text search when issue fixed
    # https://github.com/coleifer/peewee/issues/1527
    # matches = Act.select().where(Match(Act.content, query))
    result = {'matches': [base_url + m.content_url for m in matches]}
    return result
