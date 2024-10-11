import os  # Standard library module for interacting with the operating system.
import gitlab  # GitLab API client for Python to interact with GitLab.
import base64  # Standard library module for encoding and decoding data in base64.
from datetime import datetime  # Standard library module for handling dates and times.
from dateutil.relativedelta import relativedelta  # Module from the dateutil library for manipulating dates with relative deltas.
from dotenv import load_dotenv  # Module from the python-dotenv library for loading environment variables from a .env file.


# Load environment variables from .env file
load_dotenv()

#gitlabusertoken = 'glpat-btTXz8hywUjxMY2D6JLw'#os.environ.get("gitlabusertoken")

#gitlabusername = 'oco2000' #os.environ.get("gitlabusername")


def calculate_expiry_date(months=11):
    # Get the current date
    current_date = datetime.now()
    
    # Calculate the expiry date by adding the specified number of months
    expiry_date = current_date + relativedelta(months=+months)
    
    # Format the date as "YYYY-MM-DD"
    expiry_date_str = expiry_date.strftime("%Y-%m-%d")
    
    return expiry_date_str
EXPIRY_DATE  = calculate_expiry_date()

PEERTESTINGBOT = 'ptbot'
# Access levels available
gitlab.GUEST_ACCESS = 10
gitlab.REPORTER_ACCESS = 20
gitlab.DEVELOPER_ACCESS = 30
gitlab.MAINTAINER_ACCESS = 40
gitlab.OWNER_ACCESS = 50 

def gitauth(gitlaburl,private_token):
    """
    Authenticates to GitLab with the provided access token.
    
    Parameters:
    - access_token: The GitLab personal access token for authentication.
    
    Returns:
    - A GitLab API client instance.
    """
    gl = gitlab.Gitlab(gitlaburl, private_token=private_token)
    gl.auth()
    return gl

def get_user_details(gitlaburl, usertoken, user_id=None):
    """
    Fetches user details and related information from GitLab.

    Parameters:
    - gitlaburl: URL of the GitLab instance.
    - usertoken: User's private token for authentication.
    - user_id: Optional; ID of the user to fetch details for. If not provided, fetches details for the authenticated user.

    Returns:
    - A dictionary containing user details and related information.
    """
    
    # Authenticate with GitLab
    gl = gitauth(gitlaburl,usertoken)
    
    # Fetch details of the specified user or the authenticated user
    user = gl.users.get(user_id) if user_id else gl.user
    
    # # Print user details for debugging
    # print(user, '==============')
    
    # Initialize lists for user-related data
    # Fetch all groups and filter those the user is a member of
    user_groups = [group.attributes for group in gl.groups.list(all=True, as_list=True)]
    
    # Construct the user details dictionary
    user_details = {
        'gitlabid': user.id,
        'username': user.username,
        'first_name': ' '.join(user.name.split()[1:]) if user.name else '',  # First name is assumed to be all parts except the first word
        'last_name': user.name.split()[0] if user.name else '',  # Last name is assumed to be the first word
        'state': user.state,
        'avatar_url': user.avatar_url,
        'web_url': user.web_url,
        'groups': user_groups,
        'department': user.department if hasattr(user, 'department') else None,  # Check if 'department' exists
    }

    return user_details

def check_project_exists(gl, project_name, project_namespace):
    """
    Check if a project exists in the given namespace.
    """
    try:
        projects = gl.projects.list(search=project_name)
        return any(project.namespace['path'] == project_namespace and project.name == project_name for project in projects)
    except gitlab.exceptions.GitlabError as e:
        print(f"Failed to check project existence: {e}")
        return False

def create_peertestingproject(gl, username):
    """
    Create a peer testing project in GitLab and generate a new access token for it.

    :param gl: An authenticated GitLab connection object.
    :param username: The username to be used as part of the project name.
    :return: A dictionary containing the project ID and the newly created access token.
    """
    
    # Create a new project in GitLab with a name based on the username, setting it to private visibility
    testingproject = gl.projects.create({
        'name': username + 'peertesting',  # Project name based on the username
        'description': 'This is the testing project',  # Description of the project
        'visibility': 'private'  # Set project visibility to private
    })
    
    # Create a new access token for the testing project
    access_token = testingproject.access_tokens.create({
        "name": PEERTESTINGBOT,  # Name of the access token (assumed to be a predefined constant)
        "scopes": ["api"],  # Scopes granted to the token, allowing full API access
        "expires_at": EXPIRY_DATE  # Expiry date for the token (assumed to be a predefined constant)

    })
    
    # Return a dictionary with the project ID and the access token
    return {'id': testingproject.id, 'gitlabaccesstoken': access_token.token}

def fork_project(gl, project_id, new_project_name=None):
    """
    Fork an existing project in GitLab, create a new access token for the forked project, 
    and create a peer testing project.

    :param gl: An authenticated GitLab connection object.
    :param project_id: The ID of the project to be forked.
    :param new_project_name: Optional new name for the forked project.
    :return: A tuple containing a success status and a dictionary with project details or an error message.
    """
    
    try:
        # Retrieve the project to be forked
        project = gl.projects.get(project_id)
        
        # Get the namespace name (username of the authenticated user)
        project_namespace = gl.user.username
        
        # If a new project name is provided, check if it already exists in the target namespace
        if new_project_name:
            project_exists = check_project_exists(gl, new_project_name, project_namespace)
            if project_exists:
                return (False, f"Project '{new_project_name}' already exists in namespace '{project_namespace}'.")
        
        # Fork the project with or without a new name
        try:
            if new_project_name:
                forked_project = project.forks.create({
                    'name': new_project_name,  # New name for the forked project
                    'path': new_project_name.lower(),  # Path for the forked project
                    'namespace': project_namespace  # Namespace for the forked project
                })
            else:
                forked_project = project.forks.create()
            
            # Retrieve the forked project details
            forked_project = gl.projects.get(forked_project.attributes['id'])
            
            # Create a new access token for the forked project with all valid scopes
            access_token = forked_project.access_tokens.create({
                "name": PEERTESTINGBOT,  # Name of the access token (assumed to be a predefined constant)
                "scopes": ["api"],  # Scopes granted to the token, allowing full API access
                "expires_at": EXPIRY_DATE  # Expiry date for the token (assumed to be a predefined constant)
            })
            
            # Create a peer testing project for the user
            userptbotproject = create_peertestingproject(gl, project_namespace)
            
            # Return the details of the forked project and the peer testing project
            return (True, {
                'id': forked_project.id,
                'original_project_id': project_id,
                'namespace': project_namespace,
                'members': [member.attributes for member in forked_project.members.list(all=True)],  # List all members of the forked project
                'gitlabaccesstoken': access_token.token,
                'branches': [branch.attributes for branch in forked_project.branches.list(all=True)],  # List all branches of the forked project
                'testingproject': userptbotproject
            })

        except gitlab.exceptions.GitlabCreateError as e:
            # Handle errors during the forking process
            return (False, f"Failed to fork project: {e.error_message}")
        
    except gitlab.exceptions.GitlabGetError as e:
        # Handle errors while retrieving the original project
        return (False, e)

def get_files_in_branch(gl, project_id, branch, folder):
    """
    Get all files in a folder (and subdirectories) along with their content from a specific branch.
    
    Parameters:
    - gl: GitLab instance
    - project_id: ID of the project
    - branch: Name of the branch
    - folder: Path to the folder
    
    Returns:
    - A list of dictionaries where each dictionary contains:
      - 'path': The path of the file
      - 'content': The content of the file
    """
    project = gl.projects.get(project_id)
    all_files = []

    def fetch_files(path):
        items = project.repository_tree(ref=branch, path=path, all=True)
        for item in items:
            if item['type'] == 'blob':  # It's a file
                file_path = item['path']
                file_content = project.files.get(file_path, ref=branch).decode().decode('utf-8')
                all_files.append({'path': file_path, 'content': file_content})
            elif item['type'] == 'tree':  # It's a directory
                fetch_files(item['path'])  # Recursive call

    fetch_files(folder)
    return all_files

# Helper function to create a file in a project
def create_file(glp, project_id, branch_name, file_path, content):
    """
    Creates a new file in a given branch of a project.
    
    Parameters:
    - glp: The GitLab API client instance.
    - project_id: The ID of the project.
    - branch_name: The name of the branch.
    - file_path: The path of the file to be created.
    - content: The content to be written in the file.
    """
    project = glp.projects.get(project_id)
    try:
        project.files.create({
            'file_path': file_path,
            'branch': branch_name,
            'content': content,
            'commit_message': f'Add {file_path}'
        })
        # The commit ID is not directly returned from the create call.
        # We need to retrieve the latest commit on the branch.
        latest_commit = project.commits.list(ref_name=branch_name, per_page=1,get_all=True)[0]
        commit_id = latest_commit.id
        return commit_id
    except gitlab.exceptions.GitlabCreateError as e:
        print(f"Failed to create file {file_path}: {e}")
        return None

def update_peertestingproject(gitlaburl,projects, username, fork_project_usernames):
    """
    Updates the 'src' and 'test' folders in all peer-testing projects by either creating branches or updating files.
    
    Parameters:
    - projects: A list of project objects.
    - username: The GitLab username of the user making the updates.
    - fork_project_usernames: A list of usernames who have forked the project.

    Returns:
    - A tuple where the first element is a boolean indicating success, and the second element is a message or data.
    """
 
    folders = ['src', 'test']  # Define the folders to update
    pcommits ={}
    for project in projects:
        commits =[]
        # Ensure the project's namespace is among the forked project usernames
        #print(fork_project_usernames,'=>\n',project['namespace'])
        if project['namespace'] in fork_project_usernames:
            # Authenticate using the project's GitLab access token
            glp = gitauth(gitlaburl,project['testingproject']['gitlabaccesstoken'])
            
            # Generate all expected branch names for the given forked project usernames
            allexpectedbranches = [f"{user}p{i}" for user in fork_project_usernames for i in range(len(fork_project_usernames))]
            
            # Get the list of branches for the current project
            branches = [branch.name for branch in glp.projects.get(project['testingproject']['id']).branches.list() if branch.name != 'main']
            #print(allexpectedbranches,'\n',branches)
            for branchname in allexpectedbranches:
                if branchname not in branches:
                    # Create the branch if it does not exist
                    branch = create_branch(glp, project['testingproject']['id'], branchname, ref='main')
                    #fetch the main branch from the forked project
                    gp = gitauth(gitlaburl,project['gitlabaccesstoken'])
                    branches = gp.projects.get(project['id']).branches.list()

                    # Access the name of the first branch
                    if branches:
                        first_branch_name = branches[0].name
                    files = get_files_in_branch(gp, project['id'], first_branch_name, '')
                    for file in files:
                        if not file['path'].startswith('test'):
                            commit_id = commit_to_branch(glp, project['testingproject']['id'], branchname, file['path'], f"Initialised file: {file['path']} in {branchname}", file['content'])
                            commits.append(commit_id)
                            print(f"Initialised file: {file['path']} in branch: {branchname}")
                        else:
                            file_path = f'test/init.txt'
                            content = 'init data'
                            commit_id = create_file(glp, project['testingproject']['id'], branchname, file_path, content)
                            commits.append(commit_id)
                            print(f"Created file: {file_path} in branch: {branchname}")
                    add_pipefiles(gitlaburl, branchname, project['testingproject']['gitlabaccesstoken'], project['testingproject']['id'])
                        
                else:
                    # For existing branches, update files based on the updated_files dictionary
                    for folder in folders:
                        if username not in glp.projects.get(project['testingproject']['id']).name:
                            folder = 'src'
                        files = get_files_in_branch(glp, project['testingproject']['id'], branchname, folder)
                        for file in files:
                            commit_id = commit_to_branch(glp, project['testingproject']['id'], branchname, file['path'], f"Updated file: {file['path']} in {branchname}", file['content'])
                            commits.append(commit_id)
                            print(f"Updated file: {file['path']} in branch: {branchname}")
                    add_pipefiles(gitlaburl, branchname, project['testingproject']['gitlabaccesstoken'], project['testingproject']['id'])
        pcommits[project['id']] = commits
    return (True, 'Update completed successfully', pcommits)

def get_forked_usernames(gl, original_project_id):
    """
    Get the usernames of users who forked a specific project.
    
    :param gl: GitLab object
    :param original_project_id: ID of the original project
    :return: List of usernames of the people who forked the project
    """
    try:
        original_project = gl.projects.get(original_project_id)
        forks = original_project.forks.list()
        usernames = [fork.owner['username'] for fork in forks]
        return usernames
    except gitlab.exceptions.GitlabError as e:
        print(f"Failed to get forked project usernames: {e}")
        return []

def commit_to_branch(gl, project_id, branch_name, file_path, commit_message, content):
    """
    Commit changes to a branch in a GitLab project.

    :param gl: Authenticated GitLab instance.
    :param project_id: ID of the project where the commit will be made.
    :param branch_name: Name of the branch to commit to.
    :param file_path: Path to the file to update or create.
    :param commit_message: Commit message.
    :param content: Content to be written to the file.
    :return: The created commit object.
    """
    project = gl.projects.get(project_id)
    
    try:
        # Check if the file exists in the branch
        project.files.get(file_path=file_path, ref=branch_name)
        action = 'update'
    except gitlab.exceptions.GitlabGetError:
        # If the file does not exist, it will be created
        action = 'create'
    
    # Prepare the commit data
    data = {
        'branch': branch_name,
        'commit_message': commit_message,
        'actions': [
            {
                'action': action,
                'file_path': file_path,
                'content': content
            }
        ]
    }
    # Create the commit
    try:
        commit = project.commits.create(data)
        print(f"Commit ID: {commit.id}")
        return commit.id
    except gitlab.exceptions.GitlabCreateError as create_error:
        print(f"Failed to create commit: {create_error}")
        return None
    except gitlab.exceptions.GitlabError as general_error:
        print(f"GitLab error: {general_error}")
        return None
    
def get_latest_commits(gl, testing_project_id, forked_project_id, forked_branch_name, testing_branch_name):
    """
    Get the latest commits from a testing project and its forked project.

    :param gl: Authenticated GitLab instance.
    :param testing_project_id: ID of the testing project.
    :param forked_project_id: ID of the forked project.
    :param forked_branch_name: Name of the branch to get commits from.
    :param testing_branch_name: Name of the branch to get commits from.
    :return: Dictionary with forked project commit ID as the key and testing project commit ID as the value.
    """
    def get_latest_commit(project, branch_name):
        try:
            # Try to get the latest commit from the specified branch
            commits = project.commits.list(ref_name=branch_name, per_page=1, get_all=True)
            if len(commits) > 0:
                return commits[0].id
            else:
                raise Exception(f"No commits found in the branch '{branch_name}'")
        except:
            # If the branch does not exist or has no commits, get the default branch
            default_branch = project.default_branch
            print(f"Branch '{branch_name}' not found or empty. Using default branch '{default_branch}' instead.")
            commits = project.commits.list(ref_name=default_branch, per_page=1, get_all=True)
            if len(commits) > 0:
                return commits[0].id
            else:
                raise Exception(f"No commits found in the default branch '{default_branch}'")

    testing_project = gl.projects.get(testing_project_id)
    forked_project = gl.projects.get(forked_project_id)
    
    # Get the latest commit from the testing project
    try:
        testing_commit_id = get_latest_commit(testing_project, testing_branch_name)
        print(f"Testing commit ID: {testing_commit_id}")
    except Exception as e:
        testing_commit_id = None
        print(f"Error getting commit from testing project: {e}")

    # Get the latest commit from the forked project
    try:
        forked_commit_id = get_latest_commit(forked_project, forked_branch_name)
        print(f"Forked commit ID: {forked_commit_id}")
    except Exception as e:
        forked_commit_id = None
        print(f"Error getting commit from forked project: {e}")

    # Return the commits in a dictionary
    commits_dict = {forked_commit_id: testing_commit_id}
    return commits_dict

def create_branch(gl, project_id, branch_name, ref='main'):
    """
    Create a branch in a GitLab project.

    :param gl: Authenticated GitLab instance.
    :param project_id: ID of the project where the branch will be created.
    :param branch_name: Name of the new branch.
    :param ref: The branch or commit to branch from (default is 'main').
    :return: The created branch object.
    """
    project = gl.projects.get(project_id)
    branch = project.branches.create({'branch': branch_name, 'ref': ref})
    return branch

def delete_project(gitlaburl, gitlabusertoken, project_id,tproject_id):
    """
    Delete a project from GitLab.

    :param gitlaburl: The URL of the GitLab instance.
    :param gitlabusertoken: The access token of the GitLab user.
    :param project_id: The ID of the project to be deleted.
    :return: True if the project was successfully deleted, False otherwise.
    """
    # Authenticate to GitLab using the provided URL and user token
    gl = gitauth(gitlaburl, gitlabusertoken,)
    
    try:
        # Attempt to delete the project using its ID
        project = gl.projects.delete(project_id)
        gl.projects.delete(tproject_id)
        
    
    except Exception as e:
        try:
            gl.projects.delete(tproject_id)
        except Exception as e:
            pass
        
    return (True,'Project deleted successfully')

def list_projects(gl, ps):
    """
    List all projects associated with the given IDs, including their branches and file structures.

    :param gl: An authenticated GitLab connection object.
    :param ids: A list of project IDs to be listed.
    :return: A list of projects with their branches and file structures.
    """
    projects = []

    for proj in ps:
        project_id = proj.id
        try:
            project = gl.projects.get(project_id)
            branches = project.branches.list(get_all=True)
            branch_data = []

            for branch in branches:
                files = project.repository_tree(recursive=True, ref=branch.name, get_all=True)
                folder_structure = create_folder_structure(files)
                branch_data.append({'name': branch.name, 'files': folder_structure})

            project_info = project.attributes
            project_info['branches'] = branch_data

            # Retrieve the list of commits in the project
            commits = project.commits.list()
            project_info['commits'] = commits
            commits = project.commits.list()
            commit_info_list = []
            for commit in commits:
                commit_info_list.append({
                    'id': commit.id,
                    'message': commit.message,
                    'author_name': commit.author_name,
                    'created_at': commit.created_at
                })
            project_info['commits'] = commit_info_list
            projects.append(project_info)


        except Exception as e:
            print(f"Error processing project {project_id}: {e}")
        
        tproject_id = proj.testingproject['id']
        try:
            tproject = gl.projects.get(tproject_id)
            tbranches = tproject.branches.list(get_all=True)
            tbranch_data = []

            for branch in tbranches:
                files = tproject.repository_tree(recursive=True, ref=branch.name, get_all=True)
                folder_structure = create_folder_structure(files)
                tbranch_data.append({'name': branch.name, 'files': folder_structure})

            tproject_info = tproject.attributes
            tproject_info['branches'] = tbranch_data
            # Retrieve the list of commits in the project
            tcommits = tproject.commits.list()
            tcommit_info_list = []
            for commit in tcommits:
                tcommit_info_list.append({
                    'id': commit.id,
                    'message': commit.message,
                    'author_name': commit.author_name,
                    'created_at': commit.created_at
                })
            tproject_info['commits'] = tcommit_info_list
            project_info['testingproject'] = tproject_info
        except Exception as e:
            print(f"Error processing testing project {tproject_id}: {e}")
    
    return projects

def create_folder_structure(files):
    """
    Create a nested folder structure from a list of file paths.

    :param files: A list of file dictionaries with 'path' keys.
    :return: A nested dictionary representing the folder structure.
    """
    folder_structure = {}
    for file in files:
        path_parts = file['path'].split('/')
        current_level = folder_structure
        for part in path_parts[:-1]:
            current_level = current_level.setdefault(part, {})
        current_level[path_parts[-1]] = file
    return folder_structure


def comment_on_commit(gitlaburl,project, commit_id, comment_text):
    """
    Add a comment to a commit in both the testing project and the main project.
    
    :param project: Dictionary containing project details and commits.
    :param commit_id: Commit ID to comment on.
    :param comment_text: Text of the comment to add.
    :return: None or exception if an error occurs.
    """
    # Authenticate to GitLab for the testing project
    gl_testing = gitauth(gitlaburl,project['testingproject']['gitlabaccesstoken'])
    if not gl_testing:
        return 'Invalid GitLab token for testing project'
    # Get the testing project
    try:
        testing_project = gl_testing.projects.get(project['testingproject']['id'])
    except gitlab.exceptions.GitlabGetError as e:
        return f'Failed to get testing project: {e}'
    
    # Authenticate to GitLab for the main project
    gl_main = gitauth(gitlaburl,project['gitlabaccesstoken'])
    if not gl_main:
        return 'Invalid GitLab token for main project'
    
    # Get the main project
    try:
        main_project = gl_main.projects.get(project['id'])
    except gitlab.exceptions.GitlabGetError as e:
        return f'Failed to get main project: {e}'

    # Add comments to the commit in both projects
    try:
        # Create the comment
        
        for commit in project['commits']:
            if commit_id in commit.keys():

                # Comment on the commit in the main project
                main_commit = main_project.commits.get(commit_id)
                main_commit.comments.create({'note': comment_text})
                
                # Comment on the commit in the testing project
                testing_commit = testing_project.commits.get(commit[commit_id])
                testing_commit.comments.create({'note': comment_text})
                
                return (True,'Comment added successfully!')
        return (False,'Commit ID not found in project commits.')
    
    except gitlab.exceptions.GitlabCreateError as e:

        return (False,e)
    
def get_comments_on_commit(gitlaburl,project_id, token, commit_id):
    """
    Get comments on a specific commit.
    
    :param project_id: ID of the GitLab project.
    :param token: GitLab personal access token.
    :param commit_id: ID of the commit to get comments for.
    :return: List of comments on the commit.
    """
    try:
        gl = gitauth(gitlaburl,token)
        if not gl:
            return None
        project = gl.projects.get(project_id)
        commit = project.commits.get(commit_id)
        comments = commit.comments.list()
        return [c.attributes for c in comments]
    except gitlab.exceptions.GitlabGetError as e:
        return []

def add_pipefiles(gitlaburl, branchname, peerbottoken, project_id):
    """
    Run tests on a specific branch in a GitLab project by creating or updating and committing test files.

    :param gitlaburl: The URL of the GitLab instance.
    :param branchname: The name of the branch to run tests on.
    :param peerbottoken: The GitLab access token for authentication.
    :param project_id: The ID of the project in which to run tests.
    :return: A dictionary containing the commit ID, branch name, peerbottoken, and project ID if successful, otherwise None.
    """
    try:
        # Authenticate to GitLab using the provided URL and access token
        gl = gitauth(gitlaburl, peerbottoken)
        
        # Get the project by its ID
        project = gl.projects.get(project_id)

        # Check if the files exist, if they do, use 'update', otherwise use 'create'
        actions = []

        for file_path, content in [
            ('.env', ''),
            ('detect_and_test.sh', open(f'{os.getcwd()}/gitlabapp/utils/detect_and_test.sh').read()),
            ('.gitlab-ci.yml', open(f'{os.getcwd()}/gitlabapp/utils/.gitlab-ci.yml').read())
        ]:
            try:
                # Attempt to get the file to see if it exists
                project.files.get(file_path=file_path, ref=branchname)
                action = 'update'
                commit_message = f'running tests on {branchname} branch'
            except gitlab.GitlabGetError:
                # If the file does not exist, it will raise a GitlabGetError
                action = 'create'
                commit_message = f'init tests on {branchname} branch'+' [ci skip]'

            actions.append({
                'action': action,
                'file_path': file_path,
                'content': content,
            })

        # Prepare the commit data
        data = {
            'branch': branchname,
            'commit_message': commit_message,
            'actions': actions,
        }

        # Create a commit with the specified data
        commit = project.commits.create(data)

        # Return a dictionary containing the commit details
        return {'id': commit.id, 'branch': branchname, 'peerbottoken': peerbottoken, 'project_id': project_id}

    except Exception as e:
        # Print the error message if an exception occurs
        print(f"An error occurred: {e}")
        return None

#print(list_projects() ) 
#print(fork_project(116,gitauth(gitlaburl,gitlabusertoken)))    
# gl = gitauth(gitlaburl,gitlabusertoken)
# print(gl.projects.list())
# print(gl.projects.get(14902).access_tokens.list())
# for token in gl.projects.get(14902).access_tokens.list():
#     print(f"Token Name: {token.name}, Token: {token.token}")
#print(delete_project('glpat-btTXz8hywUjxMY2D6JLw',16337)) #last # 337

#print(list_project_branches(16023))
# project_id = 16039
# files = get_files_in_branch(project_id,'main')
# print(f"Files in branch '{gitlabusername}':")
# for file_info in files:
#     if file_info['type'] == 'blob':  # Only process files (not directories)
#         file_path = file_info['path']
#         print(f"Reading file: {file_path}")
#         file_content = get_file_content(project_id, file_path, gitlabusername)
#         if file_content is not None:
#             print(f"Content of {file_path}:\n{file_content}\n")
#         else:
#             print(f"Failed to read content of {file_path}\n")

# Example usage
# user_id = 977  # Replace with the actual user ID or None for authenticated user

# user_details = get_user_details(gitlabusertoken,user_id)
# print(user_details)

#print(comment_on_commit(16040, 'af7f9b5f', '⭐⭐⭐⭐⭐This is a nice comment @oco2000 ')) #tags with 5 star rating
