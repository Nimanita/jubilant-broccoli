import pytest
import json
from datetime import datetime
from app.users.models import User
from app.users.schemas import user_registration_schema, user_login_schema
from marshmallow import ValidationError


class TestUserModel:
    """Test class for User model functionality."""
    
    def test_user_creation(self, db_session):
        """Test basic user creation."""
        user = User(username='testuser')
        user.set_password('testpassword123')
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.password_hash is not None
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)
    
    def test_user_password_hashing(self, db_session):
        """Test password hashing functionality."""
        user = User(username='hashtest')
        original_password = 'mypassword123'
        
        # Set password
        user.set_password(original_password)
        
        # Password should be hashed
        assert user.password_hash != original_password
        assert len(user.password_hash) > 0
        
        # Should be able to check correct password
        assert user.check_password(original_password) is True
        
        # Should reject incorrect password
        assert user.check_password('wrongpassword') is False
        assert user.check_password('') is False
        assert user.check_password('MyPassword123') is False  # Case sensitive
    
    def test_user_password_hash_consistency(self, db_session):
        """Test that password hashing is consistent but unique."""
        user1 = User(username='user1')
        user2 = User(username='user2')
        
        same_password = 'samepassword123'
        user1.set_password(same_password)
        user2.set_password(same_password)
        
        # Both should verify the same password
        assert user1.check_password(same_password) is True
        assert user2.check_password(same_password) is True
        
        # But hashes should be different (due to salt)
        assert user1.password_hash != user2.password_hash
    
    def test_user_to_dict_method(self, sample_user):
        """Test user to_dict method."""
        user_dict = sample_user.to_dict()
        
        # Should include these fields
        required_fields = ['id', 'username', 'created_at']
        for field in required_fields:
            assert field in user_dict
        
        # Should not include sensitive fields
        sensitive_fields = ['password', 'password_hash']
        for field in sensitive_fields:
            assert field not in user_dict
        
        # Check values
        assert user_dict['id'] == sample_user.id
        assert user_dict['username'] == sample_user.username
        
        # created_at should be in ISO format
        assert isinstance(user_dict['created_at'], str)
        # Should be able to parse the ISO date
        datetime.fromisoformat(user_dict['created_at'].replace('Z', '+00:00'))
    
    def test_user_repr_method(self, sample_user):
        """Test user __repr__ method."""
        repr_str = repr(sample_user)
        assert '<User' in repr_str
        assert sample_user.username in repr_str
        assert repr_str.endswith('>')
    
    def test_user_unique_username_constraint(self, db_session):
        """Test that username must be unique."""
        # Create first user
        user1 = User(username='uniquetest')
        user1.set_password('password123')
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with same username
        user2 = User(username='uniquetest')
        user2.set_password('anotherpassword123')
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
        
        db_session.rollback()
    
    def test_user_username_nullable_constraint(self, db_session):
        """Test that username cannot be null."""
        user = User()
        user.set_password('password123')
        db_session.add(user)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
        
        db_session.rollback()
    
    def test_user_password_hash_nullable_constraint(self, db_session):
        """Test that password_hash cannot be null."""
        user = User(username='nopassword')
        # Don't set password
        db_session.add(user)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
        
        db_session.rollback()
    
    def test_user_relationship_with_inspections(self, db_session, sample_user):
        """Test user relationship with inspections."""
        from app.inspections.models import Inspections
        
        # Create inspections for the user
        inspection1 = Inspections(
            vehicle_number='REL123',
            damage_report='Testing user-inspection relationship',
            image_url='https://example.com/rel1.jpg',
            inspected_by=sample_user.id
        )
        
        inspection2 = Inspections(
            vehicle_number='REL456',
            damage_report='Another inspection for relationship testing',
            image_url='https://example.com/rel2.jpg',
            inspected_by=sample_user.id
        )
        
        db_session.add_all([inspection1, inspection2])
        db_session.commit()
        
        # Test that user has access to inspections through relationship
        assert len(sample_user.inspections) == 2
        assert inspection1 in sample_user.inspections
        assert inspection2 in sample_user.inspections
        
        # Test that inspections have reference to user
        assert inspection1.inspector == sample_user
        assert inspection2.inspector == sample_user


class TestUserSchemas:
    """Test class for user validation schemas."""
    
    def test_user_registration_schema_valid_data(self):
        """Test user registration schema with valid data."""
        valid_data = {
            'username': 'validuser123',
            'password': 'validpassword123'
        }
        
        result = user_registration_schema.load(valid_data)
        assert result['username'] == 'validuser123'
        assert result['password'] == 'validpassword123'
    
    def test_user_registration_schema_username_validation(self):
        """Test username validation in registration schema."""
        # Test minimum length (3 characters)
        valid_min = {'username': 'abc', 'password': 'password123'}
        result = user_registration_schema.load(valid_min)
        assert result['username'] == 'abc'
        
        # Test maximum length (50 characters)
        valid_max = {'username': 'a' * 50, 'password': 'password123'}
        result = user_registration_schema.load(valid_max)
        assert result['username'] == 'a' * 50
        
        # Test username too short
        with pytest.raises(ValidationError) as exc_info:
            user_registration_schema.load({'username': 'ab', 'password': 'password123'})
        assert 'username' in exc_info.value.messages
        
        # Test username too long
        with pytest.raises(ValidationError) as exc_info:
            user_registration_schema.load({'username': 'a' * 51, 'password': 'password123'})
        assert 'username' in exc_info.value.messages
    
    def test_user_registration_schema_username_regex_validation(self):
        """Test username regex validation."""
        valid_usernames = [
            'validuser',
            'user123',
            'user_name',
            'User_123',
            'UPPERCASE',
            'a1b2c3'
        ]
        
        for username in valid_usernames:
            data = {'username': username, 'password': 'password123'}
            result = user_registration_schema.load(data)
            assert result['username'] == username
        
        invalid_usernames = [
            'user@name',
            'user.name', 
            'user-name',
            'user name',
            'user#name',
            'user$name',
            'user!name'
        ]
        
        for username in invalid_usernames:
            data = {'username': username, 'password': 'password123'}
            with pytest.raises(ValidationError) as exc_info:
                user_registration_schema.load(data)
            assert 'Username can only contain letters, numbers, and underscores' in str(exc_info.value.messages)
    
    def test_user_registration_schema_password_validation(self):
        """Test password validation in registration schema."""
        # Test minimum length (6 characters)
        valid_min = {'username': 'testuser', 'password': '123456'}
        result = user_registration_schema.load(valid_min)
        assert result['password'] == '123456'
        
        # Test maximum length (128 characters)
        valid_max = {'username': 'testuser', 'password': 'a' * 128}
        result = user_registration_schema.load(valid_max)
        assert result['password'] == 'a' * 128
        
        # Test password too short
        with pytest.raises(ValidationError) as exc_info:
            user_registration_schema.load({'username': 'testuser', 'password': '12345'})
        assert 'password' in exc_info.value.messages
        
        # Test password too long
        with pytest.raises(ValidationError) as exc_info:
            user_registration_schema.load({'username': 'testuser', 'password': 'a' * 129})
        assert 'password' in exc_info.value.messages
    
    def test_user_registration_schema_required_fields(self):
        """Test required field validation in registration schema."""
        # Missing username
        with pytest.raises(ValidationError) as exc_info:
            user_registration_schema.load({'password': 'password123'})
        assert 'username' in exc_info.value.messages
        
        # Missing password
        with pytest.raises(ValidationError) as exc_info:
            user_registration_schema.load({'username': 'testuser'})
        assert 'password' in exc_info.value.messages
        
        # Empty data
        with pytest.raises(ValidationError) as exc_info:
            user_registration_schema.load({})
        assert 'username' in exc_info.value.messages
        assert 'password' in exc_info.value.messages
    
    def test_user_login_schema_valid_data(self):
        """Test user login schema with valid data."""
        valid_data = {
            'username': 'loginuser',
            'password': 'loginpassword'
        }
        
        result = user_login_schema.load(valid_data)
        assert result['username'] == 'loginuser'
        assert result['password'] == 'loginpassword'
    
    def test_user_login_schema_required_fields(self):
        """Test required field validation in login schema."""
        # Missing username
        with pytest.raises(ValidationError) as exc_info:
            user_login_schema.load({'password': 'password123'})
        assert 'username' in exc_info.value.messages
        
        # Missing password
        with pytest.raises(ValidationError) as exc_info:
            user_login_schema.load({'username': 'testuser'})
        assert 'password' in exc_info.value.messages
        
        # Empty data
        with pytest.raises(ValidationError) as exc_info:
            user_login_schema.load({})
        assert 'username' in exc_info.value.messages
        assert 'password' in exc_info.value.messages
    
    def test_user_login_schema_no_validation_rules(self):
        """Test that login schema doesn't apply registration validation rules."""
        # Login schema should accept any string for username and password
        # It doesn't enforce length or format restrictions
        
        data = {
            'username': 'a',  # Would be invalid for registration
            'password': '1'   # Would be invalid for registration
        }
        
        result = user_login_schema.load(data)
        assert result['username'] == 'a'
        assert result['password'] == '1'
    
    def test_schema_dump_functionality(self, sample_user):
        """Test schema dump functionality."""
        # Registration schema doesn't typically dump, but test if it can handle user data
        user_data = {
            'username': sample_user.username,
            'password': 'dummypassword'  # This wouldn't be the real password
        }
        
        # Load and then dump
        loaded_data = user_registration_schema.load(user_data)
        dumped_data = user_registration_schema.dump(loaded_data)
        
        assert dumped_data['username'] == sample_user.username
        assert 'password' in dumped_data


class TestUserEdgeCases:
    """Test class for user edge cases and error conditions."""
    
    def test_user_password_with_special_characters(self, db_session):
        """Test password handling with special characters."""
        user = User(username='specialchar')
        special_password = 'P@ssw0rd!#$%^&*()_+-=[]{}|;:,.<>?'
        
        user.set_password(special_password)
        db_session.add(user)
        db_session.commit()
        
        assert user.check_password(special_password) is True
        assert user.check_password('P@ssw0rd!#$%^&*()_+-=[]{}|;:,.<>') is False  # Missing last char
    
    def test_user_password_with_unicode_characters(self, db_session):
        """Test password handling with unicode characters."""
        user = User(username='unicode')
        unicode_password = 'pässwörd123ñ'
        
        user.set_password(unicode_password)
        db_session.add(user)
        db_session.commit()
        
        assert user.check_password(unicode_password) is True
        assert user.check_password('password123') is False
    
    def test_user_username_boundary_cases(self):
        """Test username validation boundary cases."""
        # Test exactly 3 characters (minimum)
        data = {'username': 'abc', 'password': 'password123'}
        result = user_registration_schema.load(data)
        assert result['username'] == 'abc'
        
        # Test exactly 50 characters (maximum)
        username_50 = 'a' * 50
        data = {'username': username_50, 'password': 'password123'}
        result = user_registration_schema.load(data)
        assert result['username'] == username_50
        
        # Test 2 characters (below minimum)
        with pytest.raises(ValidationError):
            user_registration_schema.load({'username': 'ab', 'password': 'password123'})
        
        # Test 51 characters (above maximum)
        with pytest.raises(ValidationError):
            user_registration_schema.load({'username': 'a' * 51, 'password': 'password123'})
    
    def test_user_password_boundary_cases(self):
        """Test password validation boundary cases."""
        # Test exactly 6 characters (minimum)
        data = {'username': 'testuser', 'password': '123456'}
        result = user_registration_schema.load(data)
        assert result['password'] == '123456'
        
        # Test exactly 128 characters (maximum)
        password_128 = 'a' * 128
        data = {'username': 'testuser', 'password': password_128}
        result = user_registration_schema.load(data)
        assert result['password'] == password_128
        
        # Test 5 characters (below minimum)
        with pytest.raises(ValidationError):
            user_registration_schema.load({'username': 'testuser', 'password': '12345'})
        
        # Test 129 characters (above maximum)
