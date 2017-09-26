import os

from peewee import *
from playhouse.db_url import connect
from dotenv import load_dotenv

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '../..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)


# Connect to the database URL defined in the environment, falling
# back to a local Sqlite database if no database URL is specified.
db = connect(os.environ.get('DATABASE_URL') or 'sqlite:///default.db')

# db_url = os.environ.get('DATABASE_URL').split('//')[1]
# user, rest = db_url.split(':')
# password, rest = rest.split('@')
# db_name = rest.split('/')[1]
# db = MySQLDatabase(db_name, user=user, password=password, charset='utf8mb4')

# https://docs.google.com/spreadsheets/d/1F-hADJqjvD2_n-g9rLd8AGbmeKUnMb9h49fmUxx0rYo/edit#gid=276135992

class BaseModel(Model):
    class Meta:
        database = db

class Category(BaseModel):
    type = CharField(unique=True)
    
    class Meta:
        db_table = 'cat_type'

class Source(BaseModel):
    ForeignKeyField(Category, related_name='type_id', null=True)
    nr = IntegerField()
    year = IntegerField()
    week = IntegerField()
    date = DateTimeField()
    url = CharField()

    class Meta:
        db_table = 'db_source'

class Item(BaseModel):
    source = ForeignKeyField(Source, null=True)
    item_number = IntegerField()
    item_description = CharField()
    subject = CharField(1000)
    unit = CharField()
    item_url = CharField()

    class Meta:
        db_table = 'db_item'

class Act(BaseModel):
    item = ForeignKeyField(Item, null=True)
    act_number = IntegerField(null=True)
    type = CharField()
    subject = CharField(1000)
    content_url = CharField(unique = True)
    content = TextField()

    class Meta:
        db_table = 'db_act'
