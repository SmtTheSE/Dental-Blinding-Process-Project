import os
from io import BytesIO
from app import create_app
from models import db, Patient

app = create_app('testing')
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

with app.test_client() as client:
    with app.app_context():
        # Setup session to bypass login and CSRF
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'supervisor'
            sess['csrf_token'] = 'testtoken'

        # Read the test file
        with open('test_bulk_import_opg.xlsx', 'rb') as f:
            file_data = f.read()

        data = {
            'csv_file': (BytesIO(file_data), 'test_bulk_import_opg.xlsx'),
            'csrf_token': 'testtoken'
        }

        # Send post request
        print("Sending POST request to /patients...")
        response = client.post('/patients', data=data, content_type='multipart/form-data')
        print(f"Response status code: {response.status_code}")

        # Verify DB insertion
        patients = Patient.query.filter(Patient.patient_id.in_(['TEST-1', 'TEST-2', 'TEST-3'])).all()
        print(f"Found {len(patients)} test patients in DB.")
        for p in patients:
            print(f"Patient {p.patient_id}: Name={p.name}, OPG={p.opg_link}")
            
        # Clean up test patients
        for p in patients:
            db.session.delete(p)
        db.session.commit()
        print("Cleaned up test patients from DB.")
