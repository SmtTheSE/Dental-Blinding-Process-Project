from app import app
from models import Patient

def check_db():
    with app.app_context():
        total = Patient.query.count()
        with_opg = Patient.query.filter(Patient.opg_link.isnot(None)).count()
        print(f"Total patients: {total}")
        print(f"Patients with OPG: {with_opg}")
        
        if with_opg > 0:
            p = Patient.query.filter(Patient.opg_link.isnot(None)).first()
            print(f"Sample OPG link: {p.opg_link}")
        else:
            print("No patients with OPG links found.")

if __name__ == "__main__":
    check_db()
