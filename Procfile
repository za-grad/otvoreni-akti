web: gunicorn otvoreni_akti.wsgi --pythonpath otvoreni_akti
beat: celery beat -A otvoreni_akti -l INFO
worker: celery worker -A otvoreni_akti -l INFO