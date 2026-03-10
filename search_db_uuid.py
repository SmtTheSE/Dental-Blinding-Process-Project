from app import create_app
from models import db, Patient, EstimationEntry, User
import sqlalchemy

app = create_app()
with app.app_context():
    target = "cabdf696-7818-4c15-ad69-a9d9abd7cddd"
    print(f"Searching for {target} in database...")
    
    # Search Patients
    patients = Patient.query.all()
    for p in patients:
        for attr, value in p.__dict__.items():
            if str(value) == target:
                print(f"Found in Patient {p.id}: {attr}")
                
    # Search Users
    users = User.query.all()
    for u in users:
        for attr, value in u.__dict__.items():
            if str(value) == target:
                print(f"Found in User {u.id}: {attr}")
                
    # Search EstimationEntry
    entries = EstimationEntry.query.all()
    for e in entries:
        for attr, value in e.__dict__.items():
            if str(value) == target:
                print(f"Found in EstimationEntry {e.id}: {attr}")

    print("Search complete.")
