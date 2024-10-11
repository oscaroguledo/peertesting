import gitlab.exceptions  # Import exceptions from the GitLab library for error handling
from .utils.utils import *  # Import all utility functions from the utils module within the current package
from rest_framework import viewsets, status  # Import viewsets and status codes from Django REST Framework
from rest_framework.views import APIView  # Import APIView class to create views for handling API requests
from rest_framework.response import Response  # Import Response class to return responses from API views
from .models import Project # Import the Project and TestInstance models from the current module
from authapp.models import User
from django.forms.models import model_to_dict  # Import model_to_dict to convert model instances to dictionaries
from .serializers import ProjectSerializer # Import serializers for the Project and TestInstance models

class StatusAPIView(APIView):
    """
    API view to check the status of the application.

    This view responds with the application name and version. 
    Useful for monitoring and ensuring that the API is operational.
    """

    def get(self, request, *args, **kwargs):
        """
        Get the status of the API.

        Post a review (comment) on a specific commit in a testing project.
        
        :param request: The HTTP request object.
        :return: JSON response with success status and message or error message.
        """
        name = 'ANONYMOUS PEER TEST/REVIEW APP'  # Set the application name
        version = '1.0.0'  # Set the application version
        data = {  # Create a dictionary to hold the response data
            'name': name,  # Include the application name
            'version': version  # Include the application version
        }
        # Return a successful response with status 200 and the data
        return Response({'success': True, "message": "Api is running", 'data': data}, status=status.HTTP_200_OK)

class ProjectViewSet(viewsets.ViewSet):
    """
    A viewset for handling CRUD operations on Project objects.

    This viewset provides methods to create, retrieve, update, list, and destroy projects
    associated with GitLab repositories.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    #Create a new project
    def create(self, request, *args, **kwargs):
        """
        Create a new project.

        This method forks a new project in GitLab, associates it with the testing project, and saves it in the database.

        :param request: The HTTP request object.
        :return: JSON response with success status and project details or error message.
        """
        gitlabaccesstoken = request.data.get("gitlabaccesstoken")
        new_project_name = request.data.get('new_project_name')
        projectid = request.data.get('projectid')
        errors = ''
        
        # Validate required fields
        if projectid is None:
            return Response({'success': False, "message": "projectid is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        if new_project_name is None:
            return Response({'success': False, "message": "new_project_name is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        if gitlabaccesstoken is None:
            return Response({'success': False, "message": "gitlabaccesstoken is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate with GitLab
        try:
            instance = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Continue with your logic if the user is found
        gl = gitauth(instance.gitlaburl,gitlabaccesstoken)
        projects = [model_to_dict(project) for project in Project.objects.filter(gitlaburl=instance.gitlaburl)]
        
        if gl:
            # Fork the project
            new_project = fork_project(gl, projectid, new_project_name)
            fork_project_usernames = get_forked_usernames(gl, projectid)
            
            if new_project[0] is True:
                projects.append(new_project[1])
                update_peertestingproject(instance.gitlaburl,projects, gl.user.username, fork_project_usernames)

                data = new_project[1]
                latest_commits = get_latest_commits(gl, new_project[1]['testingproject']['id'], new_project[1]['id'], 'main', gl.user.username + 'p0')
                data['commits'] = [latest_commits]
                data['gitlaburl']=instance.gitlaburl
                serializer = ProjectSerializer(data=data)
                
                if serializer.is_valid():
                    project = serializer.save()
                    response_data = {
                        'success': True,
                        'message': f'Project forked successfully',
                        'data': serializer.data
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    errors = serializer.errors
            else:
                errors = new_project[1]
        else:
            errors = "Invalid gitlabaccesstoken"
                
        return Response({
            'success': False,
            'message': 'Failed to create Project',
            'data': errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    #Retrieve a project
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific project.

        This method retrieves the details of a specific project from GitLab.

        :param request: The HTTP request object.
        :param pk: Primary key of the project to retrieve.
        :return: JSON response with success status and project details or error message.
        """
        gitlabaccesstoken = request.query_params.get("gitlabaccesstoken")
        project_id = pk
        
        # Validate required fields
        if project_id is None:
            return Response({'success': False, "message": "project_id is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        if gitlabaccesstoken is None:
            return Response({'success': False, "message": "gitlabaccesstoken is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate with GitLab
        try:
            user = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Continue with your logic if the user is found
        gl = gitauth(user.gitlaburl, gitlabaccesstoken)
        
        p = {}
        
        if gl:
            try:
                project = gl.projects.get(project_id)
            except gitlab.exceptions.GitlabGetError as e:
                print(f"Error retrieving project: {e}")
                return Response({'success': False, "message": "project not found", 'data': None}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                project2 = gl.projects.get(gl, int(project_id) + 1)
                project.update({'testingproject': project2})
                p = project
            except gitlab.exceptions.GitlabGetError as e:
                try:
                    project2 = gl.projects.get(int(project_id) - 1)
                    project2.update({'testingproject': project})
                    p = project2
                except gitlab.exceptions.GitlabGetError as e:
                    print(f"Error retrieving testing project: {e}")
                    return Response({'success': False, "message": "testing project not found", 'data': None}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'success': True, "message": "project retrieved successfully", 'data': p}, status=status.HTTP_200_OK)
        
        return Response({'success': False, "message": "gitlabaccesstoken is invalid", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
    
    #Update a project
    def update(self, request, *args, **kwargs):
        """
        Update a project.

        This method commits changes to a specific branch of the project in GitLab.

        :param request: The HTTP request object.
        :param kwargs: Additional arguments.
        :return: JSON response with success status and project details or error message.
        """
        partial = kwargs.pop('partial', False)
        
        try:
            instance = Project.objects.get(pk=kwargs['pk'])
        except Project.DoesNotExist:
            return Response({'success': False, "message": "Project not found", 'data': None}, status=status.HTTP_404_NOT_FOUND)
        
        instance_dict = model_to_dict(instance)
        
        # Get required fields from request data
        branch_name = request.data.get('branch_name')
        project_id = instance_dict['id']
        file_path = request.data.get('file_path')
        commit_message = request.data.get('commit_message')+' [ci skip]'
        content = request.data.get('content')+"""import unittest
                                                        from src.main import hello_world

                                                        class TestMain(unittest.TestCase):
                                                            def test_hello_world(self):
                                                                self.assertEqual(hello_world(), 'Hello, World!')

                                                        if __name__ == '__main__':
                                                            unittest.main()
                                                        """
        gitlabaccesstoken = request.data.get('gitlabaccesstoken')
        
        # Validation
        required_fields = [
            ('gitlabaccesstoken', gitlabaccesstoken),
            ('file_path', file_path),
            ('commit_message', commit_message),
            ('content', content),
            ('projectid', project_id),
            ('branch_name', branch_name)
        ]
        
        for field_name, field_value in required_fields:
            if field_value is None:
                return Response({'success': False, "message": f"{field_name} is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate with GitLab
        try:
            user = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Continue with your logic if the user is found
        gl = gitauth(user.gitlaburl,gitlabaccesstoken)
        if not gl:
            return Response({'success': False, "message": "Invalid GitLab token", 'data': None}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Commit to branch
        try:
            project_commit_id = commit_to_branch(gl, project_id, branch_name, file_path, commit_message, content)
        except Exception as e:
            return Response({'success': False, "message": str(e), 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get forked project usernames
        try:
            fork_project_usernames = get_forked_usernames(gl, instance_dict['original_project_id'])
        except Exception as e:
            return Response({'success': False, "message": str(e), 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update peer testing project
        try:
            projects = [model_to_dict(project) for project in Project.objects.all()]
            _, _, pcommits = update_peertestingproject(projects, gl.user.username, fork_project_usernames, content)
        except Exception as e:
            return Response({'success': False, "message": str(e), 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update commits in the instance
        try:
            for p in pcommits.keys():
                if p == project_id:
                    instance.commits = {project_commit_id: pcommits[p]}
                    instance.save()
        except Exception as e:
            return Response({'success': False, "message": str(e), 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            'success': True,
            'message': 'Project updated successfully',
            'data': None
        }
        return Response(response_data)
    
    #List the projects
    def list(self, request, *args, **kwargs):
        """
        List all projects.

        This method retrieves a list of all projects associated with the provided GitLab username.

        :param request: The HTTP request object.
        :return: JSON response with success status and list of projects or error message.
        """
        gitlabaccesstoken = request.query_params.get("gitlabaccesstoken")
        
        # Validate required fields
        if gitlabaccesstoken is None:
            return Response({'success': False, "message": "gitlabaccesstoken is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate with GitLab
        try:
            user = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Continue with your logic if the user is found
        gl = gitauth(user.gitlaburl, gitlabaccesstoken)
        if gl:
            # Retrieve only the IDs of all Project objects and Convert the QuerySet to a list
            projects = Project.objects.filter()

            # Fetch all projects
            projects = list_projects(gl, projects)
            return Response({'success': True, "message": "project retrieved successfully", 'data': projects}, status=status.HTTP_200_OK)
        
        return Response({'success': False, "message": "gitlabaccesstoken is invalid", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
    
    #Destroy a project
    def destroy(self, request,*args, **kwargs):
        """
        Delete a project.

        This method deletes the project from both the database and GitLab.

        :param request: The HTTP request object.
        :param kwargs: Additional arguments.
        :return: JSON response with success status or error message.
        """
        instance = Project.objects.get(id=kwargs['pk'])
        gitlabaccesstoken = request.query_params.get("gitlabaccesstoken")
        
        project = model_to_dict(instance)
        
        # Validate required fields
        if gitlabaccesstoken is None:
            return Response({'success': False, "message": "gitlabaccesstoken is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete project in GitLab
        try:
            user = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
    
        # Continue with your logic if the user is found
        d = delete_project(user.gitlaburl,gitlabaccesstoken, int(instance.id), int(instance.testingproject['id']))
        if d[0] == False:
            return Response({'success': False, "message": "project not deleted successfully", 'data': None}, status=status.HTTP_403_FORBIDDEN)
        
        # Delete project in the database
        instance.delete()
        
        response_data = {
            'success': True,
            'message': 'Project deleted successfully',
            'data': None
        }
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

class Comment(APIView):
    """
    API view to handle posting and retrieving comments on commits in testing projects.

    This view allows users to post comments on specific commits in a testing project
    and retrieve comments for a specific commit.
    """
    #Create a new Comment
    def post(self, request, *args, **kwargs):
        """
        Post a review (comment) on a specific commit in a testing project.

        :param request: The HTTP request object.
        :return: JSON response with success status and message or error message.
        """
        project_id = request.data.get("project_id")
        commit_id = request.data.get("commit_id")
        comment_text = request.data.get("comment_text")
        gitlabaccesstoken =request.data.get("gitlabaccesstoken")
        # Check if project_id is provided
        if project_id is None:
            return Response({'success': False, "message": "project_id is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        # Check if commit_id is provided
        if commit_id is None:
            return Response({'success': False, "message": "commit_id is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        # Check if comment_text is provided
        if comment_text is None:
            return Response({'success': False, "message": "comment_text is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        if not gitlabaccesstoken:
            return Response({'success':False,'message':'gitlabaccesstoken is needed'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Retrieve all projects and convert them to dictionaries
            projects = [model_to_dict(project) for project in Project.objects.all()]

            # Loop through projects to find the matching testing project
            res = (False,None)
            
            for project in projects:
                if project['id'] == int(project_id):
                    # Post the comment on the commit
                    c = comment_on_commit(user.gitlaburl,project, commit_id, comment_text+' [ci skip]')
                    res= c
            # Return success response if comment is posted successfully
            return Response({'success': res[0], "message": res[1], 'data': None}, status=status.HTTP_200_OK)

        except Exception as e:
            # Return error response if an exception occurs
            return Response({'success': False, "message": str(e), 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #Retrieve Comments
    def get(self, request, *args, **kwargs):
        """
        Get comments on a specific commit in a project.

        :param request: The HTTP request object.
        :return: JSON response with success status and comments or error message.
        """
        project_id = request.query_params.get("project_id")
        commit_id = request.query_params.get("commit_id")
        gitlabaccesstoken =request.query_params.get("gitlabaccesstoken")
        # Check if testingproject_id is provided
        if project_id is None:
            return Response({'success': False, "message": "project_id is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        # Check if commit_id is provided
        if commit_id is None:
            return Response({'success': False, "message": "commit_id is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        if not gitlabaccesstoken:
            return Response({'success':False,'message':'gitlabaccesstoken is needed'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Retrieve all projects and convert them to dictionaries
            projects = [model_to_dict(project) for project in Project.objects.all()]

            # Find the matching testing project and retrieve the access token
            matching_project = next(
                (project for project in projects if project['id'] == int(project_id)),
                None
            )

            if matching_project:
                gitlabaccesstoken = matching_project['gitlabaccesstoken']
                
                # Get comments on the specified commit
                comments = get_comments_on_commit(user.gitlaburl, project_id, gitlabaccesstoken, commit_id)
                comments = [comment for comment in comments if not '⭐' in comment['note']]
                # Return response with found comments
                return Response({'success': True, "message": "comments found", 'data': comments}, status=status.HTTP_200_OK)

            # Return a response if no matching project is found
            return Response({'success': False, "message": "Project not found", 'data': None}, status=status.HTTP_404_NOT_FOUND)

        except Project.DoesNotExist:
            # Return response if testing project does not exist
            return Response({'success': False, "message": "Project not found", 'data': None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Return error response if an exception occurs
            return Response({'success': False, "message": str(e), 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Review(APIView):
    """
    API view to handle posting and retrieving Reviews on commits in testing projects.

    This view allows users to post Reviews on specific commits in a testing project
    and retrieve Reviews for a specific commit.
    """
    #Create a Review on a commit
    def post(self, request, *args, **kwargs):
        """
        Post a review (comment) on a specific commit in a testing project.
        
        :param request: The HTTP request object.
        :return: JSON response with success status and message or error message.
        """
        # Retrieve and validate required data from the request
        project_id = request.data.get("project_id")
        commit_id = request.data.get("commit_id")
        comment_text = request.data.get("comment_text")
        gitlabaccesstoken = request.data.get("gitlabaccesstoken")
        rating = request.data.get("rating")

        if not project_id:
            return Response({'success': False, "message": "project_id is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        if not gitlabaccesstoken:
            return Response({'success': False, "message": "gitlabaccesstoken is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        if not commit_id:
            return Response({'success': False, "message": "commit_id is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        if not comment_text:
            return Response({'success': False, "message": "comment_text is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
    
        if int(rating) not in (1,2,3,4,5):
            return Response({'success': False, "message": "rating must be between 1 to 5", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepend rating stars to the comment text
        comment_text = f"{'⭐' * rating} {comment_text}"

        try:
            user = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Retrieve all projects and convert them to dictionaries
            projects = [model_to_dict(project) for project in Project.objects.all()]

            # Loop through projects to find the matching testing project
            res = (False,None)
            
            for project in projects:
                if project['id'] == int(project_id):
                    # Post the comment on the commit
                    c = comment_on_commit(user.gitlaburl,project, commit_id, comment_text+' [ci skip]')
                    res= c
            # Return success response if comment is posted successfully
            return Response({'success': res[0], "message": 'Review added successfully', 'data': None}, status=status.HTTP_200_OK)

        except Exception as e:
            # Return error response if an exception occurs
            return Response({'success': False, "message": str(e), 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #Retrieve Reviews on a commit
    def get(self, request, *args, **kwargs):
        """
        Get reviews on a specific commit in a project.

        :param request: The HTTP request object.
        :return: JSON response with success status and reviews or error message.
        """
        project_id = request.query_params.get("project_id")
        commit_id = request.query_params.get("commit_id")
        gitlabaccesstoken =request.query_params.get("gitlabaccesstoken")
        # Check if testingproject_id is provided
        if project_id is None:
            return Response({'success': False, "message": "project_id is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        # Check if commit_id is provided
        if commit_id is None:
            return Response({'success': False, "message": "commit_id is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        
        if not gitlabaccesstoken:
            return Response({'success':False,'message':'gitlabaccesstoken is needed'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Retrieve all projects and convert them to dictionaries
            projects = [model_to_dict(project) for project in Project.objects.all()]

            # Find the matching testing project and retrieve the access token
            matching_project = next(
                (project for project in projects if project['id'] == int(project_id)),
                None
            )

            if matching_project:
                gitlabaccesstoken = matching_project['gitlabaccesstoken']
                
                # Get comments on the specified commit
                reviews = get_comments_on_commit(user.gitlaburl, project_id, gitlabaccesstoken, commit_id)
                
                # Filter comments that contain a rating (indicated by '⭐')
                reviews = [review for review in reviews if '⭐' in review['note']]
                
                return Response({'success': True, "message": "reviews retrieved successfully", 'data': reviews}, status=status.HTTP_200_OK)
        
            # Return a response if no matching project is found
            return Response({'success': False, "message": "Project not found", 'data': None}, status=status.HTTP_404_NOT_FOUND)

        except Project.DoesNotExist:
            # Return response if testing project does not exist
            return Response({'success': False, "message": "Project not found", 'data': None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Return error response if an exception occurs
            return Response({'success': False, "message": str(e), 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TestViewSet(viewsets.ModelViewSet):
    """
    A viewset for handling CRUD operations on TestInstance Pipelines.

    This viewset provides methods to create, list, and retrieve test instances
    associated with commits in testing projects.
    """
    #Trigger a Test
    def create(self, request, *args, **kwargs):
        """
        Create a new test instance.

        This method creates a new test instance for a specific branch in a testing project.
        It checks the existence of the branch and runs the test on that branch.

        :param request: The HTTP request object.
        :return: JSON response with success status and test result or error message.
        """
        testingproject_id = request.data.get("testingproject_id")
        branchname = request.data.get("branchname")
        gitlabaccesstoken =  request.data.get("gitlabaccesstoken")

        if not gitlabaccesstoken:
            return Response({'success':False, "message":'gitlabaccesstoken is required', 'data':None}, status=status.HTTP_400_BAD_REQUEST)

        if not testingproject_id:
            return Response({'success': False, "message": "testingproject_id is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        if not branchname:
            return Response({'success': False, "message": "branchname is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        project = None
        try:
            for proj in Project.objects.all():
                if proj.testingproject['id'] == testingproject_id:
                    project = proj

        except Project.DoesNotExist:
            return Response({'success': False, "message": "project not found", 'data': None}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            user = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Continue with your logic if the user is found
        gl = gitauth(user.gitlaburl,gitlabaccesstoken)
        if gl is None:
            return Response({'success': False, "message": "gitlabusertoken is invalid", 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        gitlab_project = gl.projects.get(testingproject_id)
        branches = gitlab_project.branches.list()
        if not any(branch.name == branchname for branch in branches):
            return Response({'success': False, "message": f"branch '{branchname}' not found in project {project.name}", 'data': None}, status=status.HTTP_404_NOT_FOUND)

        t = add_pipefiles(user.gitlaburl, branchname, gitlabaccesstoken, gitlab_project.id)
        if t is not None: 
            return Response({'success': True, "message": "test executed successfully", 'data': t}, status=status.HTTP_200_OK)

        return Response({'success': False, "message": "test failed", 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #List the Tests
    def list(self, request, *args, **kwargs):
        """
        List test instances.

        This method lists all test instances for a specific branch in a testing project.

        :param request: The HTTP request object.
        :return: JSON response with success status and list of test instances or error message.
        """
        testingproject_id = request.query_params.get("testingproject_id")
        branchname = request.query_params.get("branchname")
        gitlabaccesstoken =request.query_params.get("gitlabaccesstoken")

        if not testingproject_id:
            return Response({'success': False, "message": "testingproject_id is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        if not branchname:
            return Response({'success': False, "message": "branchname is required", 'data': None}, status=status.HTTP_400_BAD_REQUEST)
        if not gitlabaccesstoken:
            return Response({'success':False,'message':'gitlabaccesstoken is needed'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Continue with your logic if the user is found
        gl = gitauth(user.gitlaburl,gitlabaccesstoken)
        gitlab_project = gl.projects.get(testingproject_id)
        pipelines = [p.attributes for p in gitlab_project.pipelines.list(all=True)]
        
        return Response({'success': True, "message": "tests retrieved successfully", 'data': pipelines}, status=status.HTTP_200_OK)
    
    #Retrieve a Test
    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Retrieve a specific test instance.

        This method retrieves details of a specific test instance based on its commit ID.

        :param request: The HTTP request object.
        :param pk: Primary key (commit ID) of the test instance to retrieve.
        :return: JSON response with success status and test instance details or error message.
        """
        gitlabaccesstoken =request.query_params.get("gitlabaccesstoken")
        pipeline_id = request.query_params.get("pipeline_id")
        testingproject_id =  request.query_params.get("testingproject_id")
        if not testingproject_id:
            return Response({"success":False,"message":"testingproject_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not pipeline_id:
            return Response({"success":False,"message":'pipeline_id is required'},status=status.HTTP_400_BAD_REQUEST)
        if not gitlabaccesstoken:
            return Response({'success':False,'message':'gitlabaccesstoken is needed'},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(gitlabusertoken=gitlabaccesstoken)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User with the provided GitLab access token does not exist',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Continue with your logic if the user is found
        gl = gitauth(user.gitlaburl,gitlabaccesstoken)
        gitlab_project = gl.projects.get(testingproject_id)
        pipeline = gitlab_project.pipelines.get(pipeline_id)

        return Response({'success': True, "message": "test retrieved successfully", 'data': pipeline}, status=status.HTTP_200_OK)
     