
# GitLab Anonymous Peer Review & Feedback Application

## Overview

The **Anonymous Peer Review and Feedback Application** allows users to anonymously submit and review feedback for GitLab projects. Users authenticate using their GitLab account and generate a Personal Access Token (PAT) for secure interactions. This app connects to GitLab to retrieve projects, submit feedback, and manage anonymous peer reviews for projects, including those belonging to organizations and individual users.

## Features

- **Anonymous Peer Review**: Users can provide feedback and reviews on GitLab projects without revealing their identity.
- **GitLab Integration**: Authenticate using a GitLab Personal Access Token to access projects and repositories.
- **Feedback Submission**: Submit anonymous feedback or reviews on specific GitLab projects by using their project ID.
- **Secure Authentication**: Utilize GitLab's OAuth or Personal Access Token (PAT) for secure user authentication.

## Requirements

- **GitLab Account**
- **Personal Access Token** (PAT) from GitLab
- **Python 3.x**
- **Django Framework**
- **Django REST Framework**

## Step 1: Generating Your Personal Access Token

Before using the app, you must generate a **Personal Access Token** from GitLab to authenticate your requests.

1. **Log in to GitLab**:
   - Go to your GitLab instance and log in with your credentials.

2. **Navigate to Personal Access Tokens Page**:
   - Go to: `https://gitlab-student.macs.hw.ac.uk/-/user_settings/personal_access_tokens`
   - Alternatively, navigate from **Settings** > **Access Tokens**.

3. **Create a New Token**:
   - **Token Name**: Enter a descriptive name (e.g., `PeerReviewAppToken`).
   - **Expiration Date**: Set the expiration date for the token.
   - **Select Scopes**:
     - `api` (for full API access).
     - `read_user` (to access user information).
     - `write_repository` (for submitting feedback on repositories).

4. **Generate Token**:
   Click **Create Personal Access Token**. **Save** the token securely since it won’t be shown again.

## Step 2: Logging In

### Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://gitlab-student.macs.hw.ac.uk/yourusername/anonymous-peer-review-app.git
cd anonymous-peer-review-app
```

### Set Up a Virtual Environment

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Set Up Environment Variables

To interact with GitLab, set up your environment variables in a `.env` file in the root directory:

```bash
GITLAB_USERNAME=your_gitlab_username
GITLAB_ACCESS_TOKEN=your_personal_access_token
```

### Apply Migrations

Run the database migrations:

```bash
python manage.py migrate
```

### Start the Server

Run the Django development server:

```bash
python manage.py runserver
```

## Step 3: Using the Application

### 1. Authentication

To use the application, you must authenticate using your GitLab username and the generated Personal Access Token.

#### API Endpoint: Login

- **Endpoint**: `/api/auth/login/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "username": "your_gitlab_username",
    "token": "your_personal_access_token"
  }
  ```

- **Response**:
  ```json
  {
    "success": true,
    "message": "Logged in successfully",
    "token": "jwt_access_token"
  }
  ```

You will receive a JWT token upon successful authentication, which you will use in the following requests.

### 2. Submitting Anonymous Peer Reviews

After logging in, you can anonymously submit feedback to any project by using its **project ID**.

#### API Endpoint: Submit Review

- **Endpoint**: `/api/projects/<project_id>/review/`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer <jwt_access_token>`
- **Payload**:
  ```json
  {
    "feedback": "Your anonymous feedback on the project."
  }
  ```

- **Response**:
  - Success:
    ```json
    {
      "success": true,
      "message": "Feedback submitted successfully",
      "data": {
        "project_id": "<project_id>",
        "feedback": "Your anonymous feedback"
      }
    }
    ```
  - Failure:
    ```json
    {
      "success": false,
      "message": "Error message",
      "data": null
    }
    ```

### 3. Retrieving Submitted Feedback

You can retrieve all anonymous feedback for a particular GitLab project.

#### API Endpoint: Get Feedback

- **Endpoint**: `/api/projects/<project_id>/reviews/`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <jwt_access_token>`

- **Response**:
  ```json
  {
    "success": true,
    "message": "Reviews retrieved successfully",
    "data": [
      {
        "review_id": 1,
        "feedback": "Anonymous review content",
        "created_at": "2023-10-10T12:34:56Z"
      },
      {
        "review_id": 2,
        "feedback": "Another anonymous review",
        "created_at": "2023-10-10T13:00:00Z"
      }
    ]
  }
  ```

## Step 4: Testing the Application

To test the application, run the following command:

```bash
python manage.py test
```

This will run the included unit tests to ensure all features are working as expected.

## Error Handling

- **500 Internal Server Error**: If there’s an issue processing the request, the server will return an error.
- **401 Unauthorized**: If authentication fails due to invalid credentials or token.
- **404 Not Found**: Returned if the specified project or resource does not exist.

## Contributing

To contribute to the project:

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
