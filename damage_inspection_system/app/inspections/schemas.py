from marshmallow import Schema, fields, validate, ValidationError, validates_schema
import re

class InspectionCreateSchema(Schema):
    vehicle_number = fields.Str(
        required=True,
        validate=[
            validate.Length(min=5, max=20),
            
        ]
    )
    damage_report = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=1000)
    )
    image_url = fields.Url(required=True)
    
    @validates_schema
    def validate_image_url(self, data, **kwargs):
        """Validate image URL extension"""
        image_url = data.get('image_url')
        if image_url:
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if not any(image_url.lower().endswith(ext) for ext in valid_extensions):
                raise ValidationError('Image URL must end with .jpg, .jpeg, or .png', field_name='image_url')

class InspectionUpdateSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf(['reviewed', 'completed'])
    )

class InspectionFilterSchema(Schema):
    status = fields.Str(
        required=False,
        validate=validate.OneOf(['pending', 'reviewed', 'completed'])
    )

# Initialize schemas
inspection_create_schema = InspectionCreateSchema()
inspection_update_schema = InspectionUpdateSchema()
inspection_filter_schema = InspectionFilterSchema()