from flask import Blueprint, request, jsonify
from app.auth.services import AuthService
from app.auth.utils import get_current_user
from app.core.logger import log_request
from flask_jwt_extended import jwt_required
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/test', methods=['GET'])
def test():
    return {"message": "Auth blueprint working!"}

@auth_bp.route('/db-test', methods=['GET'])
def db_test():
    try:
        from app.extensions import db
        from sqlalchemy import text
        with db.engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            return {"message": "Database connection successful!", "result": "Connected to MySQL"}
    except Exception as e:
        return {"error": f"Database connection failed: {str(e)}"}

@auth_bp.route('/signup', methods=['POST'])
@log_request
def signup():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        response, status_code = AuthService.register_user(data)
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Signup endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
@log_request
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        response, status_code = AuthService.login_user(data)
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Login endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
@log_request
def get_profile():
    """Get current user profile (protected route)"""
    try:
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'message': 'Profile retrieved successfully',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Profile endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500