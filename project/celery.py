from __future__ import absolute_import, unicode_literals
import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('smm_bicycle')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app = Celery()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5 * 60.0, test.s('hello'), name='Check for posts')
