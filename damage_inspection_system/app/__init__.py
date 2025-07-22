from flask import Flask
from app.extensions import db, migrate, jwt, bcrypt
from app.config import Config
from app.core.logger import setup_logger

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Setup logging
    setup_logger()
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    
   # Register blueprints
    from app.auth.routes import auth_bp
    from app.inspections.routes import inspections_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(inspections_bp)
    
    # Import models to ensure they're registered with SQLAlchemy
    from app.users.models import User
    from app.inspections.models import Inspections
    
    
    return app