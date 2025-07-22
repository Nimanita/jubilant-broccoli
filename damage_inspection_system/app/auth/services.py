from app.extensions import db
from app.users.models import User
from app.users.schemas import user_registration_schema, user_login_schema
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)

class AuthService:
    
    @staticmethod
    def register_user(data):
        """Register a new user"""
        try:
            # Validate input data
            validated_data = user_registration_schema.load(data)
            
            # Check if username already exists
            existing_user = User.query.filter_by(username=validated_data['username']).first()
            if existing_user:
                return {'error': 'Username already exists'}, 400
            
            # Create new user
            user = User(username=validated_data['username'])
            user.set_password(validated_data['password'])
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {user.username}")
            
            return {
                'message': 'User registered successfully',
                'user': user.to_dict()
            }, 201
            
        except ValidationError as e:
            logger.error(f"Registration validation error: {e.messages}")
            return {'error': e.messages}, 400
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            db.session.rollback()
            return {'error': 'Registration failed'}, 500
    
    @staticmethod
    def login_user(data):
        """Authenticate user and return JWT token"""
        try:
            # Validate input data
            validated_data = user_login_schema.load(data)
            
            # Find user by username
            user = User.query.filter_by(username=validated_data['username']).first()
            
            if not user or not user.check_password(validated_data['password']):
                logger.warning(f"Failed login attempt for username: {validated_data['username']}")
                return {'error': 'Invalid username or password'}, 401
            
            # Create JWT token
            access_token = create_access_token(identity=user.id)
            
            logger.info(f"User logged in: {user.username}")
            
            return {
                'message': 'Login successful',
                'access_token': access_token,
                'user': user.to_dict()
            }, 200
            
        except ValidationError as e:
            logger.error(f"Login validation error: {e.messages}")
            return {'error': e.messages}, 400
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {'error': 'Login failed'}, 500