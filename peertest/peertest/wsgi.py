"""
WSGI config for peertestapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

# Import the os module to interact with the operating system
import os

# Import Django's WSGI application handler
from django.core.wsgi import get_wsgi_application

# Set the default settings module for the 'peertestapp' project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peertestapp.settings')

# Get the WSGI application for the project
application = get_wsgi_application()
