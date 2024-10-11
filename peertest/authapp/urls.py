# Import necessary modules and classes
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# Create a router object for registering view sets
router = DefaultRouter()

# Register the UserViewSet with the router
router.register(r'', UserViewSet)

# Define the urlpatterns list to include the routes managed by the router
urlpatterns = [
    path('', include(router.urls)),  # Include the router's URLs under the base path
]
