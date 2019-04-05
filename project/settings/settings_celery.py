CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TIMEZONE = 'Europe/Moscow'
CELERYBEAT_SCHEDULE = {
    'make_posts': {
        'task': 'smm_admin.tasks.make_posts',
        'schedule': 60.0 * 5,
    }
}
