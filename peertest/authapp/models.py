import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from .utils import Util

# Custom User Manager for handling user creation
class CustomUserManager(BaseUserManager):
    # Internal method to create a user
    def _create_user(self, gitlaburl, gitlabusertoken, username, password, **extra_fields):
        # Ensure that all required fields are provided
        if not gitlaburl:
            raise ValueError("Your GitLab URL must be provided")
        if not gitlabusertoken:
            raise ValueError("Your GitLab User Token must be provided")
        if not username:
            raise ValueError("Username is not provided")
        if not password:
            raise ValueError("Password is not provided")

        # Create a user instance with the provided data
        user = self.model(gitlaburl=gitlaburl, gitlabusertoken=gitlabusertoken, username=username, **extra_fields)
        
        # Hash the password using a utility function
        user.password = Util.hash_password(password)
        
        # Save the user instance to the database
        user.save(using=self._db)
        return user
    
    # Method to create a regular user
    def create_user(self, gitlaburl, gitlabusertoken, username, password, **extra_fields):
        # Set default values for a regular user
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_superuser', False)
        
        # Call the internal method to create the user
        return self._create_user(gitlaburl, gitlabusertoken, username, password, **extra_fields)
    
    # Method to create a superuser
    def create_superuser(self, gitlaburl, gitlabusertoken, username, password, **extra_fields):
        # Set default values for a superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        
        # Call the internal method to create the superuser
        return self._create_user(gitlaburl, gitlabusertoken, username, password, **extra_fields)

# Custom User model
class User(AbstractBaseUser, PermissionsMixin):
    # Define the fields for the User model
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier for each user
    username = models.CharField(max_length=255, unique=True)  # Username field, must be unique
    gitlabid = models.CharField(max_length=255, blank=True, null=True)  # Unique GitLab ID for the user
    email = models.EmailField(max_length=255, unique=True)  # Email field, must be unique
    gitlabusertoken = models.CharField(max_length=255, unique=True)  # GitLab user token for authentication
    gitlaburl = models.URLField(max_length=255, blank=True, null=True)  # GitLab URL associated with the user
    first_name = models.CharField(max_length=240, null=True, blank=True)  # Optional first name field
    last_name = models.CharField(max_length=255, null=True, blank=True)  # Optional last name field
    password = models.CharField(max_length=255)  # Password field
    avatar_url = models.URLField(null=True, blank=True)  # Optional field for the user's avatar URL
    web_url = models.URLField(null=True, blank=True)  # Optional field for the user's web profile URL
    state = models.CharField(max_length=200, null=True, blank=True)  # Optional field for the user's state
    phonenumber = models.CharField(max_length=200, null=True, blank=True)  # Optional field for the user's phone number
    is_staff = models.BooleanField(default=False)  # Boolean flag for staff status
    is_active = models.BooleanField(default=False)  # Boolean flag for active status
    is_superuser = models.BooleanField(default=False)  # Boolean flag for superuser status
    groups = models.JSONField(null=True, blank=True)  # Optional JSON field for the user's groups
    department = models.JSONField(null=True, blank=True)  # Optional JSON field for the user's department
    followers = models.JSONField(null=True, blank=True)  # Optional JSON field for the user's followers
    following = models.JSONField(null=True, blank=True)  # Optional JSON field for the users the user is following
    date_joined = models.CharField(max_length=200, null=True, blank=True)  # Optional date joined field
    updatedAt = models.CharField(max_length=200, null=True, blank=False)  # Optional updated at field
    last_login = models.DateTimeField(auto_now=True)  # Field that stores the last login time, auto-updates

    # Link the custom user manager to the model
    objects = CustomUserManager()

    # Define the unique identifier for the user model
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['gitlabusertoken']

    class Meta:
        verbose_name = 'User'  # Human-readable name for the model
        verbose_name_plural = 'Users'  # Human-readable plural name for the model

    def __str__(self):
        return self.username  # String representation of the user object
    
    # Method to verify the user's password
    def verify_password(self, provided_password):
        # Compare the provided password with the stored hashed password
        return Util.verify_password(self.password, provided_password)
