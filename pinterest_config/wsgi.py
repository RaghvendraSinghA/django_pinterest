"""
WSGI config for pinterest_config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pinterest_config.settings")

# If DJANGO_SETTINGS_MODULE isn't already set, set it to pinterest_config.settings.
# This is an environment variable that tells Django:
# "Which settings module should I use for this project?"

application = get_wsgi_application()

#  get_wsgi_application ,"Django, create the WSGI application for this project."
