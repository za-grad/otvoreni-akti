## Development

Set up a virtualenv:

```bash
python3 -m venv --prompt otvoreni-akti .venv
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
psql postgres -p 5432 -c "create user otvoreniakti with password 'otvoreniakti';"
psql postgres -p 5432 -c "create database otvoreniakti encoding 'utf8' template template0 owner otvoreniakti;"
psql otvoreniakti -p 5432 -c "create extension hstore;"
```

Then when normally developing:

```bash
honcho -f Procfile.dev start
```

Scrape the web and populate Django DB:

```bash
python manage.py migrate
python manage.py shell
from otvoreni_akti.apps.scraper import scrape
```

Running Elasticsearch:

Download and install Elasticsearch from the [official website](https://www.elastic.co/downloads/elasticsearch).
Then run this command:
```bash
python manage.py search_index --rebuild
```


Run the Django server (if not running):
```bash
python manage.py runserver
```