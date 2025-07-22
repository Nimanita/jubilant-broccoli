from flask import Blueprint, request, jsonify
from app.inspections.services import InspectionService
from app.auth.utils import get_current_user
from app.core.logger import log_request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

logger = logging.getLogger(__name__)

inspections_bp = Blueprint('inspections', __name__, url_prefix='/api')

@inspections_bp.route('/inspection', methods=['POST'])
@jwt_required()
@log_request
def create_inspection():
    """Create a new inspection entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get current user ID from JWT token
        user_id = get_jwt_identity()
        
        response, status_code = InspectionService.create_inspection(data, user_id)
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Create inspection endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@inspections_bp.route('/inspection/<int:inspection_id>', methods=['GET'])
@jwt_required()
@log_request
def get_inspection(inspection_id):
    """Get inspection details by ID (only if created by the logged-in user)"""
    try:
        # Get current user ID from JWT token
        user_id = get_jwt_identity()
        
        response, status_code = InspectionService.get_inspection(inspection_id, user_id)
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Get inspection endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@inspections_bp.route('/inspection/<int:inspection_id>', methods=['PATCH'])
@jwt_required()
@log_request
def update_inspection_status(inspection_id):
    """Update inspection status to reviewed or completed"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get current user ID from JWT token
        user_id = get_jwt_identity()
        
        response, status_code = InspectionService.update_inspection_status(inspection_id, data, user_id)
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Update inspection endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@inspections_bp.route('/inspection', methods=['GET'])
@jwt_required()
@log_request
def get_inspections():
    """Get all inspections with optional status filtering"""
    try:
        # Get query parameters for filtering
        filters = {}
        status = request.args.get('status')
        if status:
            filters['status'] = status
        
        # Get current user ID from JWT token
        user_id = get_jwt_identity()
        
        response, status_code = InspectionService.get_user_inspections(user_id, filters)
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Get inspections endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500