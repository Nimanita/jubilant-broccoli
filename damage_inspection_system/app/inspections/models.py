from app.extensions import db
from datetime import datetime
from enum import Enum

class InspectionStatus(Enum):
    PENDING = 'pending'
    REVIEWED = 'reviewed'
    COMPLETED = 'completed'
    
    
class Inspections(db.Model):
    __tablename__ = 'inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), nullable=False)
    damage_report = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text , nullable=False)
    inspected_by = db.Column(db.Integer , db.ForeignKey('users.id'), nullable=False)
  # PostgreSQL uses VARCHAR for Enum, this is compatible
    status = db.Column(db.Enum(InspectionStatus, name='inspection_status'), 
                      default=InspectionStatus.PENDING, nullable=False)    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with User model
    inspector = db.relationship('User', backref='inspections', lazy=True)
   
    def to_dict(self):
            """Convert inspection to dictionary"""
            return {
                'id': self.id,
                'vehicle_number': self.vehicle_number,
                'inspected_by': self.inspected_by,
                'damage_report': self.damage_report,
                'status': self.status.value,
                'image_url': self.image_url,
                'created_at': self.created_at.isoformat(),
                'inspector_username': self.inspector.username if self.inspector else None
            }
        
    def __repr__(self):
            return f'<Inspection {self.id} - {self.vehicle_number}>'