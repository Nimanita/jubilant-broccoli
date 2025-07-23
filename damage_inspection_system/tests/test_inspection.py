import pytest
import json
from app.inspections.models import Inspections, InspectionStatus


class TestInspectionEndpoints:
    """Test class for inspection endpoints."""
    
    def test_create_inspection_success(self, client, db_session, sample_user, auth_headers, sample_inspection_data):
        """Test successful inspection creation."""
        response = client.post('/api/inspection',
                             data=json.dumps(sample_inspection_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Inspection created successfully'
        assert 'inspection' in response_data
        assert response_data['inspection']['vehicle_number'] == sample_inspection_data['vehicle_number']
        assert response_data['inspection']['damage_report'] == sample_inspection_data['damage_report']
        assert response_data['inspection']['image_url'] == sample_inspection_data['image_url']
        assert response_data['inspection']['status'] == 'pending'
        assert response_data['inspection']['inspected_by'] == sample_user.id
        
        # Verify inspection was created in database
        inspection = Inspections.query.filter_by(vehicle_number='ABC123').first()
        assert inspection is not None
        assert inspection.inspected_by == sample_user.id
    
    def test_create_inspection_no_auth(self, client, db_session, sample_inspection_data):
        """Test inspection creation without authentication."""
        response = client.post('/api/inspection',
                             data=json.dumps(sample_inspection_data),
                             content_type='application/json')
        
        assert response.status_code == 401
    
    def test_create_inspection_invalid_token(self, client, db_session, sample_inspection_data):
        """Test inspection creation with invalid token."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.post('/api/inspection',
                             data=json.dumps(sample_inspection_data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 422
    
    def test_create_inspection_missing_vehicle_number(self, client, db_session, auth_headers):
        """Test inspection creation without vehicle number."""
        data = {
            'damage_report': 'Front bumper has significant scratches',
            'image_url': 'https://example.com/damage_image.jpg'
        }
        
        response = client.post('/api/inspection',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Inspection creation failed'
    
        
    def test_update_inspection_missing_status(self, client, db_session, auth_headers, sample_inspection):
        """Test updating inspection without status field."""
        data = {'other_field': 'value'}
        
        response = client.patch(f'/api/inspection/{sample_inspection.id}',
                              data=json.dumps(data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Failed to update inspection'
    
    def test_update_inspection_no_auth(self, client, db_session, sample_inspection):
        """Test updating inspection without authentication."""
        data = {'status': 'reviewed'}
        
        response = client.patch(f'/api/inspection/{sample_inspection.id}',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 401
    
    def test_get_all_inspections_success(self, client, db_session, sample_user, auth_headers, multiple_inspections):
        """Test getting all inspections for a user."""
        response = client.get('/api/inspection', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'inspections' in response_data
        assert 'count' in response_data
        
        # Should return 3 inspections for sample_user (excluding the one from another_user)
        assert response_data['count'] == 3
        assert len(response_data['inspections']) == 3
        
        # Verify all inspections belong to the user
        for inspection in response_data['inspections']:
            assert inspection['inspected_by'] == sample_user.id
    
    def test_get_inspections_filter_by_pending_status(self, client, db_session, sample_user, auth_headers, multiple_inspections):
        """Test getting inspections filtered by pending status."""
        response = client.get('/api/inspection?status=pending', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['count'] == 1
        assert response_data['inspections'][0]['status'] == 'pending'
        assert response_data['inspections'][0]['vehicle_number'] == 'PENDING123'
    
    def test_get_inspections_filter_by_reviewed_status(self, client, db_session, sample_user, auth_headers, multiple_inspections):
        """Test getting inspections filtered by reviewed status."""
        response = client.get('/api/inspection?status=reviewed', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['count'] == 1
        assert response_data['inspections'][0]['status'] == 'reviewed'
        assert response_data['inspections'][0]['vehicle_number'] == 'REVIEWED123'
    
    def test_get_inspections_filter_by_completed_status(self, client, db_session, sample_user, auth_headers, multiple_inspections):
        """Test getting inspections filtered by completed status."""
        response = client.get('/api/inspection?status=completed', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['count'] == 1
        assert response_data['inspections'][0]['status'] == 'completed'
        assert response_data['inspections'][0]['vehicle_number'] == 'COMPLETED123'
    
    def test_get_inspections_filter_invalid_status(self, client, db_session, auth_headers, multiple_inspections):
        """Test getting inspections with invalid status filter."""
        response = client.get('/api/inspection?status=invalid_status', headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Failed to retrieve inspections'
    
    def test_get_inspections_no_auth(self, client, db_session):
        """Test getting inspections without authentication."""
        response = client.get('/api/inspection')
        
        assert response.status_code == 401
    
    def test_get_inspections_empty_result(self, client, db_session, auth_headers):
        """Test getting inspections when user has no inspections."""
        response = client.get('/api/inspection', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['count'] == 0
        assert response_data['inspections'] == []
    
    def test_get_inspections_order_by_created_at_desc(self, client, db_session, sample_user, auth_headers, multiple_inspections):
        """Test that inspections are returned in descending order of creation time."""
        response = client.get('/api/inspection', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        inspections = response_data['inspections']
        assert len(inspections) > 1
        
        # Check that inspections are ordered by created_at descending
        for i in range(len(inspections) - 1):
            current_time = inspections[i]['created_at']
            next_time = inspections[i + 1]['created_at']
            assert current_time >= next_time


class TestInspectionModel:
    """Test class for Inspection model functionality."""
    
    def test_inspection_creation_with_defaults(self, db_session, sample_user):
        """Test inspection creation with default values."""
        inspection = Inspections(
            vehicle_number='MODEL123',
            damage_report='Test damage for model testing',
            image_url='https://example.com/model_test.jpg',
            inspected_by=sample_user.id
        )
        
        db_session.add(inspection)
        db_session.commit()
        
        assert inspection.id is not None
        assert inspection.status == InspectionStatus.PENDING
        assert inspection.created_at is not None
        assert inspection.inspected_by == sample_user.id
    
    def test_inspection_status_enum_values(self, db_session, sample_user):
        """Test all InspectionStatus enum values."""
        # Test PENDING
        inspection1 = Inspections(
            vehicle_number='ENUM1',
            damage_report='Testing enum values',
            image_url='https://example.com/enum1.jpg',
            inspected_by=sample_user.id,
            status=InspectionStatus.PENDING
        )
        
        # Test REVIEWED
        inspection2 = Inspections(
            vehicle_number='ENUM2',
            damage_report='Testing enum values',
            image_url='https://example.com/enum2.jpg',
            inspected_by=sample_user.id,
            status=InspectionStatus.REVIEWED
        )
        
        # Test COMPLETED
        inspection3 = Inspections(
            vehicle_number='ENUM3',
            damage_report='Testing enum values',
            image_url='https://example.com/enum3.jpg',
            inspected_by=sample_user.id,
            status=InspectionStatus.COMPLETED
        )
        
        db_session.add_all([inspection1, inspection2, inspection3])
        db_session.commit()
        
        assert inspection1.status == InspectionStatus.PENDING
        assert inspection2.status == InspectionStatus.REVIEWED
        assert inspection3.status == InspectionStatus.COMPLETED
        
        assert inspection1.status.value == 'pending'
        assert inspection2.status.value == 'reviewed'
        assert inspection3.status.value == 'completed'
    
    def test_inspection_to_dict(self, db_session, sample_user, sample_inspection):
        """Test inspection to_dict method."""
        inspection_dict = sample_inspection.to_dict()
        
        required_fields = [
            'id', 'vehicle_number', 'inspected_by', 'damage_report',
            'status', 'image_url', 'created_at', 'inspector_username'
        ]
        
        for field in required_fields:
            assert field in inspection_dict
        
        assert inspection_dict['id'] == sample_inspection.id
        assert inspection_dict['vehicle_number'] == sample_inspection.vehicle_number
        assert inspection_dict['inspected_by'] == sample_inspection.inspected_by
        assert inspection_dict['damage_report'] == sample_inspection.damage_report
        assert inspection_dict['status'] == sample_inspection.status.value
        assert inspection_dict['image_url'] == sample_inspection.image_url
        assert inspection_dict['inspector_username'] == sample_user.username
    
    def test_inspection_repr(self, sample_inspection):
        """Test Inspection model string representation."""
        repr_string = repr(sample_inspection)
        assert str(sample_inspection.id) in repr_string
        assert sample_inspection.vehicle_number in repr_string
        assert '<Inspection' in repr_string
    
    def test_inspection_relationship_with_user(self, db_session, sample_user, sample_inspection):
        """Test the relationship between Inspection and User models."""
        # Test accessing inspector from inspection
        assert sample_inspection.inspector == sample_user
        assert sample_inspection.inspector.username == sample_user.username
        
        # Test accessing inspections from user
        assert sample_inspection in sample_user.inspections
        assert len(sample_user.inspections) >= 1
    
    def test_inspection_cascade_delete_protection(self, db_session, sample_user, sample_inspection):
        """Test that deleting user doesn't cascade delete inspections (foreign key constraint)."""
        inspection_id = sample_inspection.id
        
        # This should raise an integrity error due to foreign key constraint
        # In a real scenario, you might want to handle this differently
        db_session.delete(sample_user)
        
        with pytest.raises(Exception):  # This should raise an integrity constraint error
            db_session.commit()
        
        db_session.rollback()
        
        # Verify inspection still exists
        inspection = Inspections.query.get(inspection_id)
        assert inspection is not None


class TestInspectionValidationSchemas:
    """Test class for inspection validation schemas."""
    
    def test_valid_image_extensions(self, client, db_session, auth_headers):
        """Test all valid image extensions."""
        valid_extensions = ['.jpg', '.jpeg', '.png']
        
        for ext in valid_extensions:
            data = {
                'vehicle_number': f'IMG{ext.upper()}123',
                'damage_report': f'Testing {ext} extension validation',
                'image_url': f'https://example.com/test{ext}'
            }
            
            response = client.post('/api/inspection',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 201, f"Failed for extension {ext}"
    
    def test_case_insensitive_image_extensions(self, client, db_session, auth_headers):
        """Test that image extension validation is case insensitive."""
        extensions = ['.JPG', '.JPEG', '.PNG', '.jpg', '.jpeg', '.png']
        
        for i, ext in enumerate(extensions):
            data = {
                'vehicle_number': f'CASE{i}',
                'damage_report': 'Testing case insensitive extension validation',
                'image_url': f'https://example.com/test{ext}'
            }
            
            response = client.post('/api/inspection',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 201, f"Failed for extension {ext}"
    
    def test_boundary_values_vehicle_number(self, client, db_session, auth_headers):
        """Test boundary values for vehicle number length."""
        # Test minimum length (5 characters)
        data_min = {
            'vehicle_number': 'A' * 5,
            'damage_report': 'Testing minimum vehicle number length',
            'image_url': 'https://example.com/min.jpg'
        }
        
        response = client.post('/api/inspection',
                             data=json.dumps(data_min),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 201
        
        # Test maximum length (20 characters)
        data_max = {
            'vehicle_number': 'A' * 20,
            'damage_report': 'Testing maximum vehicle number length',
            'image_url': 'https://example.com/max.jpg'
        }
        
        response = client.post('/api/inspection',
                             data=json.dumps(data_max),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 201
    
    def test_boundary_values_damage_report(self, client, db_session, auth_headers):
        """Test boundary values for damage report length."""
        # Test minimum length (10 characters)
        data_min = {
            'vehicle_number': 'MINRPT123',
            'damage_report': 'A' * 10,
            'image_url': 'https://example.com/minrpt.jpg'
        }
        
        response = client.post('/api/inspection',
                             data=json.dumps(data_min),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 201
        
        # Test maximum length (1000 characters)
        data_max = {
            'vehicle_number': 'MAXRPT123',
            'damage_report': 'A' * 1000,
            'image_url': 'https://example.com/maxrpt.jpg'
        }
        
        response = client.post('/api/inspection',
                             data=json.dumps(data_max),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 201
    
    def test_create_inspection_vehicle_number_too_short(self, client, db_session, auth_headers):
        """Test inspection creation with vehicle number too short."""
        data = {
            'vehicle_number': 'A1',  # Less than 5 characters
            'damage_report': 'Front bumper has significant scratches',
            'image_url': 'https://example.com/damage_image.jpg'
        }
        
        response = client.post('/api/inspection',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Inspection creation failed'
    
    def test_create_inspection_vehicle_number_too_long(self, client, db_session, auth_headers):
        """Test inspection creation with vehicle number too long."""
        data = {
            'vehicle_number': 'A' * 21,  # More than 20 characters
            'damage_report': 'Front bumper has significant scratches',
            'image_url': 'https://example.com/damage_image.jpg'
        }
        
        response = client.post('/api/inspection',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Inspection creation failed'
    
    def test_create_inspection_damage_report_too_short(self, client, db_session, auth_headers):
        """Test inspection creation with damage report too short."""
        data = {
            'vehicle_number': 'ABC123',
            'damage_report': 'Short',  # Less than 10 characters
            'image_url': 'https://example.com/damage_image.jpg'
        }
        
        response = client.post('/api/inspection',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Inspection creation failed'
    
    def test_create_inspection_damage_report_too_long(self, client, db_session, auth_headers):
        """Test inspection creation with damage report too long."""
        data = {
            'vehicle_number': 'ABC123',
            'damage_report': 'A' * 1001,  # More than 1000 characters
            'image_url': 'https://example.com/damage_image.jpg'
        }
        
        response = client.post('/api/inspection',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Inspection creation failed'
    
    def test_create_inspection_invalid_image_url(self, client, db_session, auth_headers):
        """Test inspection creation with invalid image URL."""
        data = {
            'vehicle_number': 'ABC123',
            'damage_report': 'Front bumper has significant scratches',
            'image_url': 'not_a_valid_url'
        }
        
        response = client.post('/api/inspection',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Inspection creation failed'
    
    def test_create_inspection_invalid_image_extension(self, client, db_session, auth_headers):
        """Test inspection creation with invalid image extension."""
        data = {
            'vehicle_number': 'ABC123',
            'damage_report': 'Front bumper has significant scratches',
            'image_url': 'https://example.com/damage_image.gif'  # Invalid extension
        }
        
        response = client.post('/api/inspection',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Inspection creation failed'
    
    
    def test_get_inspection_success(self, client, db_session, sample_user, auth_headers, sample_inspection):
        """Test successful inspection retrieval."""
        response = client.get(f'/api/inspection/{sample_inspection.id}',
                            headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'inspection' in response_data
        assert response_data['inspection']['id'] == sample_inspection.id
        assert response_data['inspection']['vehicle_number'] == sample_inspection.vehicle_number
        assert response_data['inspection']['damage_report'] == sample_inspection.damage_report
    
    def test_get_inspection_not_found(self, client, db_session, auth_headers):
        """Test inspection retrieval with non-existent ID."""
        response = client.get('/api/inspection/999999',
                            headers=auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Inspection not found or access denied'
    
    def test_get_inspection_access_denied(self, client, db_session, sample_inspection, another_auth_headers):
        """Test inspection retrieval by different user (access denied)."""
        response = client.get(f'/api/inspection/{sample_inspection.id}',
                            headers=another_auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Inspection not found or access denied'
    
    def test_get_inspection_no_auth(self, client, db_session, sample_inspection):
        """Test inspection retrieval without authentication."""
        response = client.get(f'/api/inspection/{sample_inspection.id}')
        
        assert response.status_code == 401
    
    def test_update_inspection_status_to_reviewed(self, client, db_session, sample_user, auth_headers, sample_inspection):
        """Test updating inspection status to reviewed."""
        data = {'status': 'reviewed'}
        
        response = client.patch(f'/api/inspection/{sample_inspection.id}',
                              data=json.dumps(data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Inspection status updated successfully'
        assert response_data['inspection']['status'] == 'reviewed'
        
        # Verify status was updated in database
        updated_inspection = Inspections.query.get(sample_inspection.id)
        assert updated_inspection.status == InspectionStatus.REVIEWED
    
    def test_update_inspection_status_to_completed(self, client, db_session, sample_user, auth_headers, sample_inspection):
        """Test updating inspection status to completed."""
        data = {'status': 'completed'}
        
        response = client.patch(f'/api/inspection/{sample_inspection.id}',
                              data=json.dumps(data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Inspection status updated successfully'
        assert response_data['inspection']['status'] == 'completed'
        
        # Verify status was updated in database
        updated_inspection = Inspections.query.get(sample_inspection.id)
        assert updated_inspection.status == InspectionStatus.COMPLETED
    
    def test_update_inspection_invalid_status(self, client, db_session, auth_headers, sample_inspection):
        """Test updating inspection with invalid status."""
        data = {'status': 'invalid_status'}
        
        response = client.patch(f'/api/inspection/{sample_inspection.id}',
                              data=json.dumps(data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Failed to update inspection'
    
    def test_update_inspection_not_found(self, client, db_session, auth_headers):
        """Test updating non-existent inspection."""
        data = {'status': 'reviewed'}
        
        response = client.patch('/api/inspection/999999',
                              data=json.dumps(data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Inspection not found or access denied'
    
    def test_update_inspection_access_denied(self, client, db_session, sample_inspection, another_auth_headers):
        """Test updating inspection by different user (access denied)."""
        data = {'status': 'reviewed'}
        
        response = client.patch(f'/api/inspection/{sample_inspection.id}',
                              data=json.dumps(data),
                              content_type='application/json',
                              headers=another_auth_headers)
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Inspection not found or access denied'