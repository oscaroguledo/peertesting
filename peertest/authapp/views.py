from rest_framework import viewsets
from .models import User  # Import the User model
from .serializers import UserSerializer, UserLoginSerializer  # Import the serializers for User
from rest_framework import status, viewsets, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny  # Import permission classes
from rest_framework.response import Response  # For sending HTTP responses
from rest_framework_simplejwt.tokens import RefreshToken  # JWT tokens for authentication
from django.contrib.auth import login, logout  # Login and logout functions for user authentication
from django.shortcuts import get_object_or_404  # Helper function to get objects or return 404
from rest_framework.decorators import action  # Decorator for custom actions in viewsets
from .utils import Util  # Utility functions for hashing and password verification
from gitlabapp.utils.utils import gitauth, get_user_details  # GitLab user detail functions

# ViewSet for handling User-related operations
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Queryset for all User objects
    serializer_class = UserSerializer  # Serializer class to convert User instances to JSON
    permission_classes = [AllowAny]  # Allow any user (authenticated or not) to access this viewset

    # Override the perform_create method to handle user creation
    def perform_create(self, serializer):
        user = serializer.save(password=self.request.data['password'])  # Save the user and hash the password
        refresh = RefreshToken.for_user(user)  # Create JWT tokens for the newly created user
        return Response({
            'success': True,  # Indicate success
            'message': 'User registered successfully',  # Success message
            'userid': user.id,  # Return the user ID
            'refresh': str(refresh),  # Return the refresh token
            'access': str(refresh.access_token)  # Return the access token
        }, status=status.HTTP_201_CREATED)  # HTTP status for created resources

    # Override the create method to include GitLab user details
    def create(self, request, *args, **kwargs):
        # Get user details from GitLab using the provided token and URL
        gitlabuserdetails = get_user_details(request.data['gitlaburl'], request.data['gitlabusertoken'])
        
        # Add additional data to the user details dictionary
        gitlabuserdetails["gitlaburl"] = request.data['gitlaburl']
        gitlabuserdetails["username"] = request.data['username']
        gitlabuserdetails["gitlabusertoken"] = request.data['gitlabusertoken']
        gitlabuserdetails['is_superuser'] = request.data['is_superuser']
        gitlabuserdetails['password'] = request.data['password']
        gitlabuserdetails['email'] = request.data['email'] 
        
        # Create a serializer instance with the updated user details
        serializer = self.get_serializer(data=gitlabuserdetails)
        
        # Check if the serializer data is valid
        if serializer.is_valid():
            return self.perform_create(serializer)  # If valid, call perform_create to save the user
        
        # If the serializer data is not valid, return an error response
        return Response({'success': False, 'message': 'Failed to register User', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # Override the retrieve method to get user details by ID
    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.queryset, pk=pk)  # Get the user or return 404 if not found
        serializer = self.get_serializer(user)  # Serialize the user data
        return Response({'success': True, 'message': 'User details retrieved successfully', 'data': serializer.data})  # Return the user data

    # Override the list method to get all users
    def list(self, request):
        serializer = self.get_serializer(self.queryset, many=True)  # Serialize all user data
        return Response({'success': True, 'message': 'Users retrieved successfully', 'data': serializer.data})  # Return the list of users

    # Override the update method to update user details
    def update(self, request, pk=None, partial=False):
        user = get_object_or_404(self.queryset, pk=pk)  # Get the user or return 404 if not found
        serializer = self.get_serializer(user, data=request.data, partial=partial)  # Prepare the serializer for updating
        
        # Check if the updated data is valid
        if serializer.is_valid():
            serializer.save()  # Save the updated user data
            return Response({'success': True, 'message': 'User updated successfully', 'data': serializer.data})  # Return success message
        
        # If invalid, return error response
        return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # Override the destroy method to delete a user
    def destroy(self, request, pk=None):
        user = get_object_or_404(self.queryset, pk=pk)  # Get the user or return 404 if not found
        user.delete()  # Delete the user from the database
        return Response({'success': True, 'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)  # Return success message
    
    # Custom action to handle user login
    @action(detail=False, methods=['post'])
    def login(self, request):
        # Initialize the login serializer with the request data
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        # Check if the serializer data is valid
        if serializer.is_valid():
            user = serializer.validated_data['user']  # Get the authenticated user
            login(request, user)  # Log the user in
            refresh = RefreshToken.for_user(user)  # Generate JWT tokens for the user
            return Response({
                'success': True,  # Indicate success
                'message': 'Login successful',  # Success message
                'user': UserSerializer(user).data,  # Return serialized user data
                'refresh': str(refresh),  # Return the refresh token
                'access': str(refresh.access_token)  # Return the access token
            }, status=status.HTTP_200_OK)  # HTTP status for successful login
        
        # If invalid credentials, return an error response
        errors = [error for values in serializer.errors.values() for error in values]
        errors = errors if len(errors) > 1 else errors[0]

        return Response({'success': False, 'message': 'Invalid credentials', 'errors': errors}, status=status.HTTP_401_UNAUTHORIZED)

    # Custom action to handle user logout
    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)  # Log the user out
        return Response({'success': True, 'message': 'Logged out successfully'}, status=status.HTTP_200_OK)  # Return success message

    @action(detail=False, methods=['post'])
    def verifygitlabuser(self, request):
        gitlabusertoken = request.data.get('gitlabusertoken')  # Get the GitLab user token
        if not gitlabusertoken:  # Check if the token is provided
            return Response({'success': False, 'message': 'GitLab user token is required'}, status=status.HTTP_400_BAD_REQUEST)  # Return error if not
        user = User.objects.filter(gitlabusertoken=gitlabusertoken).first()  # Find the user with the provided token
        if user:

            gitlabuserdetails = get_user_details(user.gitlaburl,gitlabusertoken)  # Retrieve GitLab user details
        
            # Check if the GitLab user details were retrieved successfully
            if gitlabuserdetails:
                return Response({'success': True, 'message': 'GitLab user details verified successfully'})  # Return details
        
        # If GitLab user details are not found, return error response
        return Response({'success': False, 'message': 'GitLab user details not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def resetpassword(self, request):
        email = request.data.get('email')  # Get the email from request data
        user = User.objects.filter(email=email).first()  # Find the user with the provided email
        
        # Check if the user exists
        if user:
            new_password = request.data.get('new_password')  # Get new password from request
            confirm_password = request.data.get('confirm_password')  # Get confirm password from request
            
            # Check if the new password and confirm password match
            if new_password != confirm_password:
                return Response({'success': False, 'message': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)  # Return error if they don't match
            
            # If they match, hash the new password and save it
            user.password = Util.hash_password(new_password)
            user.save()  # Save the updated user data
            return Response({'success': True, 'message': 'Password reset successful'}, status=status.HTTP_200_OK)  # Return success message
        
        # If the user with the provided email does not exist, return error response
        return Response({'success': False, 'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

