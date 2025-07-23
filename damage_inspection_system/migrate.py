from app import create_app
from app.extensions import db
from flask_migrate import upgrade

def deploy():
    """Run deployment tasks."""
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Run any pending migrations
        try:
            upgrade()
        except Exception as e:
            print(f"Migration error (might be expected for first deployment): {e}")

if __name__ == '__main__':
    deploy()