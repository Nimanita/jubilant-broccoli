from flask_jwt_extended import get_jwt_identity
from app.users.models import User

def get_current_user():
    """Get current authenticated user from JWT token"""
    current_user_id = get_jwt_identity()
    return User.query.get(current_user_id)