from rest_framework import serializers
from .utils import Util
from .models import User 

# Custom authentication function to authenticate a user by username and password
def authenticate(username=None, password=None, **kwargs):
    try:
        # Try to get the user with the provided username
        user = User.objects.get(username=username)
        # If the password is verified, return the user
        if user.verify_password(password):
            return user
    except User.DoesNotExist:
        # If the user does not exist, return None
        return None

# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'  # Serialize all fields of the User model

    # Create a new user
    def create(self, validated_data):
        # Extract additional fields from the validated data
        gitlaburl = validated_data.pop('gitlaburl', None)
        gitlabusertoken = validated_data.pop('gitlabusertoken', None)
        username = validated_data.pop('username', None)
        is_superuser = validated_data.pop('is_superuser', False)
        password = validated_data.pop('password', None)
        # phonenumber = validated_data.pop('phonenumber', None)
        
        # Create a superuser if is_superuser is True, otherwise create a regular user
        if is_superuser:
            user = User.objects.create_superuser(gitlaburl =gitlaburl, gitlabusertoken=gitlabusertoken, username=username, password=password, **validated_data)
        else:
            user = User.objects.create_user(gitlaburl=gitlaburl, gitlabusertoken=gitlabusertoken, username=username, password=password, **validated_data)
        
        return user

    # Update an existing user
    def update(self, instance, validated_data):
        # Extract the password from the validated data if present
        password = validated_data.pop('password', None)
        
        # Update the instance with the remaining validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If a new password is provided, hash it before updating the instance
        if password:
            instance.password = Util.hash_password(password)

        # Save the updated instance
        instance.save()
        return instance

# Serializer for user login
class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField()  # Username field
    password = serializers.CharField()  # Password field

    # Validate the login credentials
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Ensure both username and password are provided
        if username and password:
            user = authenticate(username=username, password=password)  # Authenticate the user
            if not user:
                # Raise validation error if authentication fails
                raise serializers.ValidationError('Unable to login with provided credentials.')
        else:
            # Raise validation error if username or password is missing
            raise serializers.ValidationError('Must include "username" and "password".')
        
        # Attach the authenticated user to the validated data
        attrs['user'] = user
        return attrs
