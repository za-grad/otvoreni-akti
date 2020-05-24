from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import environ
env = environ.Env()

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'otvoreni_akti.settings')

app = Celery('otvoreni_akti')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
