## Development

Set up a virtualenv:

```bash
python3 -m venv .venv --prompt skupstina
source ./.venv/bin/activate
pip install -r requirements.txt
```

Copy and modify the config file to your liking:

```bash
cp .env.example .env
cp Procfile.dev.example Procfile.dev
```

Set up the database:

```bash
mkdir -p tmp/postgres
initdb tmp/postgres
postgres -D tmp/postgres -p 5432
psql postgres -p 5432 -c "create user skupstina with password 'skupstina';"
psql postgres -p 5432 -c "create database skupstina encoding 'utf8' template template0 owner skupstina;"
psql skupstina -p 5432 -c "create extension hstore;"
```

Then when normally developing:

```bash
honcho -f Procfile.dev start
```

Scrape the web:

```bash
python scrape.py
```

Fill the database using peewee (option 1):
```bash
python fill_db.py
```

Fill the database using Django (option 2):
```bash
cd skupstina_django
manage.py shell
from skupstina import fill_django_db
```