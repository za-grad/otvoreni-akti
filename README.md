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

Scrape and fill the database:

```bash
python scrape.py
python fill_db.py
```
