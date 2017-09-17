from skupstina.schema import db, Act

from playhouse.postgres_ext import Match

def search(query):
    result = Act.select().where(Match(Act.content, query))
    return result
