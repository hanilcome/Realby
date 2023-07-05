"""
WSGI config for Realby_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# import dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Realby_project.settings')

# dotenv.read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

application = get_wsgi_application()
