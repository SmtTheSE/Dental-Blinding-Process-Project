from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Check if default users exist, if not create them
    supervisor = User.query.filter_by(username='supervisor').first()
    pi = User.query.filter_by(username='pi').first()
    
    if not supervisor and not pi:
        # Create default users
        supervisor = User(
            username='supervisor',
            password=generate_password_hash('supervisor'),
            role='supervisor'
        )
        db.session.add(supervisor)
        
        pi = User(
            username='pi',
            password=generate_password_hash('pi'),
            role='pi'
        )
        db.session.add(pi)
        
        db.session.commit()
        print('Database setup complete! Tables created and default users added.')
    else:
        print('Default users already exist. No changes made.')