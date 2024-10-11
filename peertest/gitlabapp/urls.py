# Import necessary modules and classes for defining URL patterns
from django.urls import path, include  # Import path and include for routing
from rest_framework.routers import DefaultRouter  # Import DefaultRouter for easy routing of viewsets
from .views import ProjectViewSet, Comment, Review, StatusAPIView,TestViewSet  # Import the view classes that will handle the requests


# Create an instance of DefaultRouter, which automatically generates URL patterns for viewsets
router = DefaultRouter()  

# Register the ProjectViewSet with the router under the 'projects' prefix
router.register(r'projects', ProjectViewSet)  

# Register the TestViewSet with the router under the 'tests' prefix; specify a basename for reverse lookups
router.register(r'tests', TestViewSet, basename='test')  

# Define the urlpatterns list to hold all the routing patterns
urlpatterns = [
    # Map the 'status/' URL path to the StatusAPIView and give it a name 'status-api'
    path('status/', StatusAPIView.as_view(), name='status-api'),  
    
    # Include the router's generated URLs; this will cover all routes for the registered viewsets
    path('', include(router.urls)),  
    
    # Map the 'comments/' URL path to the Comment view and give it a name 'comment'
    path('comments/', Comment.as_view(), name='comment'),  
    
    # Map the 'reviews/' URL path to the Review view and give it a name 'review-api'
    path('reviews/', Review.as_view(), name='review'),  
]



