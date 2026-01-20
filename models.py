from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Increased length to accommodate longer hashes
    role = db.Column(db.String(20), nullable=False)  # 'supervisor' or 'pi'
    locked_until = db.Column(db.DateTime, nullable=True)  # For account lockout functionality
    failed_attempts = db.Column(db.Integer, default=0)  # Track failed login attempts
    last_login = db.Column(db.DateTime, nullable=True)  # Track last successful login
    
    def __repr__(self):
        return f'<User {self.username}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Participant identifier (T1, T2, T3, ...)
    patient_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Participant's name
    name = db.Column(db.String(100), nullable=True)
    
    # Age as recorded (integer years)
    actual_age = db.Column(db.Float, nullable=False)
    
    # Participant's sex (M/F)
    sex = db.Column(db.String(10), nullable=False)  # 'male' or 'female'
    
    # Thumbnail or link to the patient's Orthopantomogram
    opg_link = db.Column(db.String(500), nullable=True)
    
    # Randomized code related to AlQahtani method
    code_a = db.Column(db.String(50), unique=True, nullable=True)
    
    # Randomized code related to Demirjian method
    code_b = db.Column(db.String(50), unique=True, nullable=True)
    
    # Estimated age using AlQahtani method (with error margin)
    alqahtani_estimated_age = db.Column(db.Float, nullable=True)
    alqahtani_error_margin = db.Column(db.Float, nullable=True)
    
    # Estimated age using Demirjian method (with error margin)
    demirjian_estimated_age = db.Column(db.Float, nullable=True)
    demirjian_error_margin = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Patient {self.patient_id}>'

class EstimationEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)  # Either code_a or code_b
    estimated_age = db.Column(db.Float, nullable=False)
    method_used = db.Column(db.String(20), nullable=False)  # 'alqahtani' or 'demirjian'
    
    # Tooth development stages
    # AlQahtani method teeth (permanent and primary)
    tooth_21_stage = db.Column(db.String(10), nullable=True)
    tooth_22_stage = db.Column(db.String(10), nullable=True)
    tooth_23_stage = db.Column(db.String(10), nullable=True)
    tooth_24_stage = db.Column(db.String(10), nullable=True)
    tooth_25_stage = db.Column(db.String(10), nullable=True)
    tooth_26_stage = db.Column(db.String(10), nullable=True)
    tooth_27_stage = db.Column(db.String(10), nullable=True)
    tooth_31_stage = db.Column(db.String(10), nullable=True)
    tooth_32_stage = db.Column(db.String(10), nullable=True)
    tooth_33_stage = db.Column(db.String(10), nullable=True)
    tooth_34_stage = db.Column(db.String(10), nullable=True)
    tooth_35_stage = db.Column(db.String(10), nullable=True)
    tooth_36_stage = db.Column(db.String(10), nullable=True)
    tooth_37_stage = db.Column(db.String(10), nullable=True)
    tooth_61_stage = db.Column(db.String(10), nullable=True)
    tooth_62_stage = db.Column(db.String(10), nullable=True)
    tooth_63_stage = db.Column(db.String(10), nullable=True)
    tooth_64_stage = db.Column(db.String(10), nullable=True)
    tooth_65_stage = db.Column(db.String(10), nullable=True)
    tooth_71_stage = db.Column(db.String(10), nullable=True)
    tooth_72_stage = db.Column(db.String(10), nullable=True)
    tooth_73_stage = db.Column(db.String(10), nullable=True)
    tooth_74_stage = db.Column(db.String(10), nullable=True)
    tooth_75_stage = db.Column(db.String(10), nullable=True)
    
    # Demirjian method teeth (permanent mandibular)
    tooth_31_demirjian = db.Column(db.String(5), nullable=True)
    tooth_32_demirjian = db.Column(db.String(5), nullable=True)
    tooth_33_demirjian = db.Column(db.String(5), nullable=True)
    tooth_34_demirjian = db.Column(db.String(5), nullable=True)
    tooth_35_demirjian = db.Column(db.String(5), nullable=True)
    tooth_36_demirjian = db.Column(db.String(5), nullable=True)
    tooth_37_demirjian = db.Column(db.String(5), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EstimationEntry {self.code}>'