import os

from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "pinterest_config.settings"
)

app = Celery("pinterest_config")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)

app.autodiscover_tasks()