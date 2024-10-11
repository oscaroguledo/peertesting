# Import the AppConfig class from django.apps
from django.apps import AppConfig  # AppConfig is the base class for configuring Django apps

# Define a new application configuration class named GitlabappConfig
class GitlabappConfig(AppConfig):
    # Set the default primary key field type for models in this app
    default_auto_field = 'django.db.models.BigAutoField'  # BigAutoField is a type of primary key field that auto-increments and can handle large values

    # Specify the name of the application
    name = 'gitlabapp'  # This is the name of the app, and it should match the name used in the INSTALLED_APPS setting
