import os
from app import create_app
from models import db, Patient
from unittest.mock import patch

openpyxl_ready = True
try:
    import openpyxl
except Exception:
    openpyxl_ready = False

if openpyxl_ready:
    os.environ['FLASK_ENV'] = 'default'
    app = create_app('default')
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            # Setup session to bypass login and CSRF
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['role'] = 'supervisor'
                sess['csrf_token'] = 'testtoken'

            print("1. Testing signed URL generation...")
            response = client.get('/generate_upload_url?filename=test.xlsx')
            print(f"Signed URL generation status: {response.status_code}")
            data = response.get_json()
            
            # Since SUPABASE env variables might not be set in the test environment,
            # this might fail with a 500, which is expected. We'll proceed with patching
            # download_file to test the actual bypass logic in /patients.
            
            print("\n2. Testing /patients Supabase path bypass...")
            data_payload = {
                'excel_supabase_path': 'temp/dummy_excel_path.xlsx',
                'csrf_token': 'testtoken'
            }

            # Read the test file
            with open('test_with_images.xlsx', 'rb') as f:
                file_data = f.read()

            with patch('utils.storage.download_file') as mock_download:
                with patch('utils.storage.delete_image') as mock_delete:
                    with patch('utils.storage.upload_image') as mock_upload:
                        mock_download.return_value = file_data
                        mock_upload.return_value = 'http://mock-supabase.url/test.jpeg'
                        mock_delete.return_value = True
                        
                        response = client.post('/patients', data=data_payload)
                        print(f"Response status: {response.status_code}")
                        
                        # Verify DB insertion
                        patients = Patient.query.filter(Patient.patient_id.like('T1_%') | Patient.patient_id.like('T2_%')).all()
                        print(f"Found {len(patients)} test patients in DB.")
                        for p in patients:
                            print(f"Patient {p.patient_id}: Name={p.name}, OPG={p.opg_link}")
                            
                        # Clean up test patients
                        for p in patients:
                            db.session.delete(p)
                        db.session.commit()
                        print("Cleaned up test patients from DB.")
                        print(f"Download mock calls: {mock_download.call_count}")
                        print(f"Delete temporary mock calls: {mock_delete.call_count}")
