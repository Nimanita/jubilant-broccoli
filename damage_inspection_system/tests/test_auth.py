import pytest
import json
from app.users.models import User


class TestAuthEndpoints:
    """Test class for authentication endpoints."""
    
    def test_signup_success(self, client, db_session):
        """Test successful user registration."""
        data = {
            'username': 'newuser',
            'password': 'newpassword123'
        }
        
        response = client.post('/api/signup', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['message'] == 'User registered successfully'
        assert 'user' in response_data
        assert response_data['user']['username'] == 'newuser'
        
        # Verify user was created in database
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.username == 'newuser'
    
    def test_signup_duplicate_username(self, client, db_session, sample_user):
        """Test registration with existing username."""
        data = {
            'username': sample_user.username,
            'password': 'anotherpassword123'
        }
        
        response = client.post('/api/signup',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Username already exists'
    
    def test_signup_invalid_username_too_short(self, client, db_session):
        """Test registration with username too short."""
        data = {
            'username': 'ab',  # Less than 3 characters
            'password': 'validpassword123'
        }
        
        response = client.post('/api/signup',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_signup_invalid_username_too_long(self, client, db_session):
        """Test registration with username too long."""
        data = {
            'username': 'a' * 51,  # More than 50 characters
            'password': 'validpassword123'
        }
        
        response = client.post('/api/signup',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_signup_invalid_username_special_chars(self, client, db_session):
        """Test registration with invalid characters in username."""
        data = {
            'username': 'user@name!',  # Contains special characters
            'password': 'validpassword123'
        }
        
        response = client.post('/api/signup',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_signup_password_too_short(self, client, db_session):
        """Test registration with password too short."""
        data = {
            'username': 'validuser',
            'password': '12345'  # Less than 6 characters
        }
        
        response = client.post('/api/signup',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_signup_missing_username(self, client, db_session):
        """Test registration without username."""
        data = {
            'password': 'validpassword123'
        }
        
        response = client.post('/api/signup',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_signup_missing_password(self, client, db_session):
        """Test registration without password."""
        data = {
            'username': 'validuser'
        }
        
        response = client.post('/api/signup',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    
    def test_signup_empty_json(self, client, db_session):
        """Test registration with empty JSON."""
        response = client.post('/api/signup',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_login_success(self, client, db_session, sample_user):
        """Test successful login."""
        data = {
            'username': sample_user.username,
            'password': 'testpassword123'
        }
        
        response = client.post('/api/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Login successful'
        assert 'access_token' in response_data
        assert 'user' in response_data
        assert response_data['user']['username'] == sample_user.username
    
    def test_login_invalid_username(self, client, db_session):
        """Test login with non-existent username."""
        data = {
            'username': 'nonexistentuser',
            'password': 'anypassword123'
        }
        
        response = client.post('/api/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Invalid username or password'
    
    def test_login_invalid_password(self, client, db_session, sample_user):
        """Test login with incorrect password."""
        data = {
            'username': sample_user.username,
            'password': 'wrongpassword123'
        }
        
        response = client.post('/api/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Invalid username or password'
    
    def test_login_missing_username(self, client, db_session):
        """Test login without username."""
        data = {
            'password': 'testpassword123'
        }
        
        response = client.post('/api/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Login failed'
    
    def test_login_missing_password(self, client, db_session, sample_user):
        """Test login without password."""
        data = {
            'username': sample_user.username
        }
        
        response = client.post('/api/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Login failed'
    
    
    def test_get_profile_success(self, client, db_session, sample_user, auth_headers):
        """Test successful profile retrieval."""
        response = client.get('/api/profile', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Profile retrieved successfully'
        assert 'user' in response_data
        assert response_data['user']['username'] == sample_user.username
        assert response_data['user']['id'] == sample_user.id
    
    def test_get_profile_no_token(self, client, db_session):
        """Test profile retrieval without JWT token."""
        response = client.get('/api/profile')
        
        assert response.status_code == 401
    
    def test_get_profile_invalid_token(self, client, db_session):
        """Test profile retrieval with invalid JWT token."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/profile', headers=headers)
        
        assert response.status_code == 422
    
    def test_get_profile_expired_token(self, client, db_session, sample_user, app):
        """Test profile retrieval with expired token."""
        with app.app_context():
            from flask_jwt_extended import create_access_token
            from datetime import timedelta
            
            # Create token that expires immediately
            expired_token = create_access_token(
                identity=sample_user.id,
                expires_delta=timedelta(seconds=-1)
            )
            
            headers = {'Authorization': f'Bearer {expired_token}'}
            response = client.get('/api/profile', headers=headers)
            
            assert response.status_code == 401
    
    def test_auth_blueprint_test_endpoint(self, client):
        """Test the auth blueprint test endpoint."""
        response = client.get('/api/test')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Auth blueprint working!'
    
    def test_password_hashing(self, db_session):
        """Test that passwords are properly hashed."""
        user = User(username='hashtest')
        password = 'testpassword123'
        user.set_password(password)
        
        # Password should be hashed, not stored in plain text
        assert user.password_hash != password
        assert len(user.password_hash) > 0
        
        # Should be able to verify the password
        assert user.check_password(password) is True
        assert user.check_password('wrongpassword') is False
    
    def test_user_to_dict_excludes_password(self, sample_user):
        """Test that to_dict method excludes password information."""
        user_dict = sample_user.to_dict()
        
        assert 'password' not in user_dict
        assert 'password_hash' not in user_dict
        assert 'username' in user_dict
        assert 'id' in user_dict
        assert 'created_at' in user_dict
    
    def test_user_repr(self, sample_user):
        """Test User model string representation."""
        repr_string = repr(sample_user)
        assert sample_user.username in repr_string
        assert '<User' in repr_string