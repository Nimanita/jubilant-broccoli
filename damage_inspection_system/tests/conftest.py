import pytest
from flask_jwt_extended import create_access_token
import os
from app import create_app
from app.extensions import db
from app.users.models import User
from app.inspections.models import Inspections, InspectionStatus

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    # Create a test configuration
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    }
    
    app = create_app(test_config)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Create a database session for the tests."""
    with app.app_context():
        # Clean up any existing data
        db.session.query(Inspections).delete()
        db.session.query(User).delete()
        db.session.commit()
        yield db.session
        
        # Clean up after test
        db.session.rollback()
        db.session.query(Inspections).delete()
        db.session.query(User).delete()
        db.session.commit()

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(username='testuser')
    user.set_password('testpassword123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def another_user(db_session):
    """Create another user for testing access controls."""
    user = User(username='anotheruser')
    user.set_password('anotherpassword123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def auth_headers(app, sample_user):
    """Create authorization headers with JWT token."""
    with app.app_context():
        access_token = create_access_token(identity=sample_user.id)
        return {'Authorization': f'Bearer {access_token}'}
    
@pytest.fixture
def another_auth_headers(app, another_user):
    """Create authorization headers for another user."""
    with app.app_context():
        access_token = create_access_token(identity=another_user.id)
        return {'Authorization': f'Bearer {access_token}'}

@pytest.fixture
def sample_inspection_data():
    """Sample inspection data for testing."""
    return {
        'vehicle_number': 'ABC123',
        'damage_report': 'Front bumper has significant scratches and dents from collision',
        'image_url': 'https://example.com/damage_image.jpg'
    }

@pytest.fixture
def sample_inspection(db_session, sample_user):
    """Create a sample inspection for testing."""
    inspection = Inspections(
        vehicle_number='TEST123',
        damage_report='Test damage report for inspection',
        image_url='https://example.com/test_image.jpg',
        inspected_by=sample_user.id
    )
    db_session.add(inspection)
    db_session.commit()
    return inspection

@pytest.fixture
def multiple_inspections(db_session, sample_user, another_user):
    """Create multiple inspections with different statuses."""
    inspections = []
    
    # Pending inspection by sample_user
    inspection1 = Inspections(
        vehicle_number='PENDING123',
        damage_report='Pending inspection report',
        image_url='https://example.com/pending.jpg',
        inspected_by=sample_user.id,
        status=InspectionStatus.PENDING
    )
    
    # Reviewed inspection by sample_user
    inspection2 = Inspections(
        vehicle_number='REVIEWED123',
        damage_report='Reviewed inspection report',
        image_url='https://example.com/reviewed.jpg',
        inspected_by=sample_user.id,
        status=InspectionStatus.REVIEWED
    )
    
    # Completed inspection by sample_user
    inspection3 = Inspections(
        vehicle_number='COMPLETED123',
        damage_report='Completed inspection report',
        image_url='https://example.com/completed.jpg',
        inspected_by=sample_user.id,
        status=InspectionStatus.COMPLETED
    )
    
    # Inspection by another user (for access control testing)
    inspection4 = Inspections(
        vehicle_number='OTHER123',
        damage_report='Other user inspection report',
        image_url='https://example.com/other.jpg',
        inspected_by=another_user.id
    )
    
    inspections.extend([inspection1, inspection2, inspection3, inspection4])
    
    for inspection in inspections:
        db_session.add(inspection)
    
    db_session.commit()
    return inspections