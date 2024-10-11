# serializers.py
from rest_framework import serializers
from .models import Project
# Define a serializer for the Project model
class ProjectSerializer(serializers.ModelSerializer):  # ProjectSerializer inherits from ModelSerializer, which provides a convenient way to create serializers
    class Meta:
        model = Project  # Specify the model that this serializer is for
        fields = '__all__'  # Include all fields from the Project model in the serialized output

    # Define how to create a new Project instance
    def create(self, validated_data):
        # Create and return a new Project instance with the validated data
        return Project.objects.create(**validated_data)

    # Define how to update an existing Project instance
    def update(self, instance, validated_data):
        # Iterate over each attribute and value in the validated data
        for attr, value in validated_data.items():
            # Set the attribute on the instance to the new value
            setattr(instance, attr, value)
        # Save the updated instance to the database
        instance.save()
        # Return the updated instance
        return instance
