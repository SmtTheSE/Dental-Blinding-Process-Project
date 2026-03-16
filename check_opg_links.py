from app import create_app
from models import db, Patient

app = create_app()
with app.app_context():
    patients = Patient.query.limit(10).all()
    for p in patients:
        print(f"Patient {p.patient_id}: OPG_LINK = {p.opg_link}")
