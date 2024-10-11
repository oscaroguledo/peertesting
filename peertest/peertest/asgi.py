"""
ASGI config for peertestapp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

# Import the os module to interact with the operating system
import os

# Import Django's ASGI application handler
from django.core.asgi import get_asgi_application

# Set the default settings module for the 'peertestapp' project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peertestapp.settings')

# Get the ASGI application for the project
application = get_asgi_application()
