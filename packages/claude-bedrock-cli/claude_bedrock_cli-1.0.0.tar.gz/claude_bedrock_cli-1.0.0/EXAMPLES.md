# Usage Examples

This document provides real-world examples of using Claude Bedrock CLI.

## File Operations

### Reading Files

```
> Read the main.py file

> Read requirements.txt and tell me what dependencies we're using

> Show me the first 50 lines of the README
```

### Writing Files

```
> Create a new file called config.yaml with basic configuration settings

> Write a Python script that fetches data from an API

> Create a .gitignore file with common Python patterns
```

### Editing Files

```
> In main.py, change the timeout from 120 to 300 seconds

> Update the version number in setup.py to 0.2.0

> Replace all instances of "username" with "user_id" in the User class
```

## Code Search and Navigation

### Finding Files

```
> Find all Python test files

> Show me all configuration files (yaml, json, toml)

> List all JavaScript files in the src directory
```

### Searching Code

```
> Search for all TODO comments in the codebase

> Find where the authenticate function is defined

> Show me all files that import boto3
```

## Command Execution

### Development Tasks

```
> Run the test suite using pytest

> Install the dependencies from requirements.txt

> Show me the git status and recent commits
```

### System Operations

```
> Create a new directory called "tests"

> Check the Python version

> Show me the disk usage of this directory
```

## Complex Tasks

### Debugging

```
> I'm getting this error when I run the script:
[paste error message]

Can you help me debug it?

> The application is slow. Can you help me profile it and find bottlenecks?

> Review the authentication code for security issues
```

### Refactoring

```
> Refactor the UserService class to follow SOLID principles

> Extract the database connection logic into a separate module

> Convert this synchronous code to use async/await
```

### Feature Development

```
> I need to add user authentication to this Flask app.
Can you help me implement:
1. Login endpoint
2. JWT token generation
3. Protected routes
4. User session management

> Create a RESTful API for a blog system with posts, comments, and users

> Add error handling and logging to all API endpoints
```

### Code Review

```
> Review the changes in user_service.py and suggest improvements

> Check this code for potential security vulnerabilities

> Analyze the performance implications of this database query
```

## Task Management

### Using Todo Lists

Claude automatically creates todo lists for complex tasks:

```
> I need to migrate this project from SQLite to PostgreSQL

Claude will create a todo list like:
1. Install PostgreSQL dependencies
2. Create database migration scripts
3. Update database connection configuration
4. Test the migration
5. Update documentation
```

You can view the todo list anytime:
```
> /todos
```

## Advanced Workflows

### Multi-Step Projects

```
> Let's create a complete Python web scraper:

1. First, find out what libraries we need
2. Create the project structure
3. Implement the scraper with error handling
4. Add unit tests
5. Create documentation

> I want to add CI/CD to this project using GitHub Actions.
Help me set up:
- Automated testing
- Code linting
- Deployment to production
```

### Code Generation

```
> Generate a complete CRUD API for a User model with:
- SQLAlchemy models
- Pydantic schemas
- FastAPI routes
- Error handling
- Input validation

> Create a React component for a user profile page with:
- Form validation
- API integration
- Loading states
- Error handling
```

### Documentation

```
> Read through the codebase and create API documentation

> Add docstrings to all functions in the utils module

> Create a user guide for this library
```

## Tips for Effective Usage

### 1. Be Specific

❌ Bad: "Fix the bug"
✅ Good: "The login function throws a KeyError when the password field is missing. Can you add validation?"

### 2. Provide Context

❌ Bad: "Add authentication"
✅ Good: "Add JWT-based authentication to the FastAPI app. Use bcrypt for password hashing and store users in PostgreSQL"

### 3. Break Down Complex Tasks

❌ Bad: "Build a complete e-commerce system"
✅ Good: "Let's start by creating the product catalog API with:
- Product model
- CRUD endpoints
- Search functionality"

### 4. Iterate

```
> Create a user registration endpoint
[Claude implements it]

> Now add email validation
[Claude updates the code]

> Add rate limiting to prevent abuse
[Claude adds rate limiting]
```

### 5. Ask for Explanations

```
> Explain how this authentication system works

> Why did you choose to use a context manager here?

> What are the trade-offs between these two approaches?
```

## Common Patterns

### Starting a New Project

```
> I want to start a new FastAPI project. Can you:
1. Create the project structure
2. Set up a virtual environment
3. Create requirements.txt with essential dependencies
4. Create a basic main.py with hello world endpoint
5. Add a README with setup instructions
```

### Code Maintenance

```
> Run the linter and fix any style issues

> Update all dependencies to their latest compatible versions

> Add type hints to the main module
```

### Testing

```
> Write unit tests for the UserService class

> Create integration tests for the API endpoints

> Add test coverage reporting
```

### Deployment

```
> Create a Dockerfile for this application

> Write a docker-compose.yml for local development

> Create Kubernetes manifests for deployment
```

## Integration Examples

### Git Workflows

```
> Show me what files have changed

> Create a commit with the recent changes

> Review the diff before committing

> Explain what this commit changed
```

### Database Operations

```
> Create a migration to add an email field to the User table

> Write a script to seed the database with test data

> Generate an ERD diagram from the SQLAlchemy models
```

### API Development

```
> Create OpenAPI documentation for these endpoints

> Add request/response examples to the API docs

> Test all API endpoints and report any issues
```

---

These examples should give you a good starting point for using Claude Bedrock CLI effectively!
