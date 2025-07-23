from app.extensions import db
from app.inspections.models import Inspections, InspectionStatus
from app.inspections.schemas import (
    inspection_create_schema, 
    inspection_update_schema, 
    inspection_filter_schema
)
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)

class InspectionService:
    
    @staticmethod
    def create_inspection(data, user_id):
        """Create a new inspection"""
        try:
            # Validate input data
            validated_data = inspection_create_schema.load(data)
            
            # Create new inspection
            inspection = Inspections(
                vehicle_number=validated_data['vehicle_number'],
                damage_report=validated_data['damage_report'],
                image_url=validated_data.get('image_url'),
                inspected_by=user_id
            )
            
            # Save to database
            db.session.add(inspection)
            db.session.commit()
            
            logger.info(f"New inspection created: {inspection.id} by user {user_id}")
            
            return {
                'message': 'Inspection created successfully',
                'inspection': inspection.to_dict()
            }, 201
            
        except ValidationError as e:
            logger.error(f"Inspection creation validation error: {e.messages}")
            return {'error': 'Inspection creation failed'}, 400
        except Exception as e:
            logger.exception(f"Inspection creation error: {str(e)}")
            db.session.rollback()
            return {'error': 'Inspection creation failed'}, 500
    
    @staticmethod
    def get_inspection(inspection_id, user_id):
        """Get inspection by ID (only if created by the user)"""
        try:
            inspection = Inspections.query.filter_by(
                id=inspection_id, 
                inspected_by=user_id
            ).first()
            
            if not inspection:
                return {'error': 'Inspection not found or access denied'}, 404
            
            logger.info(f"Inspection {inspection_id} retrieved by user {user_id}")
            
            return {
                'inspection': inspection.to_dict()
            }, 200
            
        except Exception as e:
            logger.exception(f"Get inspection error: {str(e)}")
            return {'error': 'Failed to retrieve inspection'}, 500
    
    @staticmethod
    def update_inspection_status(inspection_id, data, user_id):
        """Update inspection status (only if created by the user)"""
        try:
            # Validate input data
            validated_data = inspection_update_schema.load(data)
            
            # Find inspection
            inspection = Inspections.query.filter_by(
                id=inspection_id, 
                inspected_by=user_id
            ).first()
            
            if not inspection:
                return {'error': 'Inspection not found or access denied'}, 404
            
            # Update status
            old_status = inspection.status.value
            inspection.status = InspectionStatus(validated_data['status'])
            
            db.session.commit()
            
            logger.info(f"Inspection {inspection_id} status updated from {old_status} to {validated_data['status']} by user {user_id}")
            
            return {
                'message': 'Inspection status updated successfully',
                'inspection': inspection.to_dict()
            }, 200
            
        except ValidationError as e:
            logger.error(f"Inspection update validation error: {e.messages}")
            return {'error': 'Failed to update inspection'}, 400
        except Exception as e:
            logger.exception(f"Inspection update error: {str(e)}")
            db.session.rollback()
            return {'error': 'Failed to update inspection'}, 500
    
    @staticmethod
    def get_user_inspections(user_id, filters=None):
        """Get all inspections for a user with optional status filtering"""
        try:
            # Build base query
            query = Inspections.query.filter_by(inspected_by=user_id)
            
            # Apply filters if provided
            if filters:
                validated_filters = inspection_filter_schema.load(filters)
                
                if 'status' in validated_filters:
                    query = query.filter_by(status=InspectionStatus(validated_filters['status']))
            
            # Execute query and get results
            inspections = query.order_by(Inspections.created_at.desc()).all()
            
            logger.info(f"Retrieved {len(inspections)} inspections for user {user_id}")
            
            return {
                'inspections': [inspection.to_dict() for inspection in inspections],
                'count': len(inspections)
            }, 200
            
        except ValidationError as e:
            logger.error(f"Inspection filter validation error: {e.messages}")
            return {'error': 'Failed to retrieve inspections'}, 400
        except Exception as e:
            logger.exception(f"Get inspections error: {str(e)}")
            return {'error': 'Failed to retrieve inspections'}, 500