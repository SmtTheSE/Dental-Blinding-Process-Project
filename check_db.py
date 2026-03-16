from app import create_app
from models import db

app = create_app()

with app.app_context():
    # Print all tables
    print("Tables in database:")
    for table in db.metadata.tables:
        print(f"  - {table}")
    
    # Print User table structure
    from models import User
    print("\nUser table columns:")
    for column in User.__table__.columns:
        print(f"  - {column.name}: {column.type}")