from marshmallow import Schema, fields, validate, ValidationError

class UserRegistrationSchema(Schema):
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=50),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error='Username can only contain letters, numbers, and underscores')
        ]
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128)
    )

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

# Initialize schemas
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()