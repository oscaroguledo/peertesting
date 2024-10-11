# Import the models module from Django
from django.db import models  # models module contains the base classes for defining database models in Django

# Create your models here.
# Define a model for representing projects in the database
class Project(models.Model):  
    # Field for the primary key, which uniquely identifies each project
    id = models.IntegerField(primary_key=True)  # An integer field that serves as the primary key for the Project model
    
    gitlaburl = models.CharField(max_length=255)
    
    # Field for storing the original project ID from another system (e.g., GitLab)
    original_project_id = models.IntegerField()  # An integer field for the original project ID, used for referencing the project in the original system
    
    # Field for storing the namespace of the project
    namespace = models.CharField(max_length=255)  # A character field for the namespace, with a maximum length of 255 characters
    
    # Field for storing the GitLab access token
    gitlabaccesstoken = models.CharField(max_length=255)  # A character field for the GitLab access token, with a maximum length of 255 characters
    
    # Field for storing the members of the project in JSON format
    members = models.JSONField(null=True)  # A JSON field for storing project members, can be null
    
    # Field for storing the branches of the project in JSON format
    branches = models.JSONField(null=True)  # A JSON field for storing branches, can be null
    
    # Field for storing the testing project details in JSON format
    testingproject = models.JSONField(null=True)  # A JSON field for storing testing project details, can be null
    
    # Field for storing the commits of the project in JSON format
    commits = models.JSONField(null=True)  # A JSON field for storing commits, can be null
