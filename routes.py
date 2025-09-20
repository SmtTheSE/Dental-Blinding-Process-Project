from flask import Blueprint, request, render_template, redirect, url_for, flash, session, Response, current_app, send_from_directory
from models import db, Patient, EstimationEntry
from dental_methods import calculate_demirjian_score, calculate_alqahtani_age, get_alqahtani_teeth, get_demirjian_teeth
from functools import wraps
from sqlalchemy import cast
import random
import string
import csv
from io import StringIO, BytesIO
import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
# Add openpyxl imports for Excel generation and reading
from openpyxl import Workbook, load_workbook
import openpyxl
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.utils import get_column_letter
# Add matplotlib for chart generation
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np

main = Blueprint('main', __name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            if session.get('role') != role and session.get('role') != 'supervisor':
                flash('Access denied')
                return redirect(url_for('main.dashboard'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

def generate_csrf_token():
    """Generate and store CSRF token in session"""
    if 'csrf_token' not in session:
        session['csrf_token'] = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    return session['csrf_token']

@main.context_processor
def inject_csrf_token():
    """Inject CSRF token into all templates"""
    return dict(csrf_token=generate_csrf_token)

def validate_csrf_token():
    """Validate CSRF token for POST requests"""
    token = session.get('csrf_token')
    form_token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
    
    if not token or not form_token or token != form_token:
        return False
    return True

@main.before_request
def csrf_protect():
    """CSRF protection for all POST requests"""
    if request.method == "POST":
        # Skip CSRF check for file uploads and API-like endpoints that might have their own protection
        if request.endpoint not in ['main.upload_opg', 'main.get_estimation_form']:
            if not validate_csrf_token():
                flash('Security token validation failed. Please try again.')
                return redirect(request.url)

@main.route('/dashboard')
@login_required
def dashboard():
    if session['role'] == 'supervisor':
        return render_template('supervisor_dashboard.html')
    else:
        return render_template('pi_dashboard.html')

def renumber_patient_ids():
    """Renumber patient IDs sequentially starting from 1"""
    patients = Patient.query.order_by(Patient.id).all()
    for i, patient in enumerate(patients, 1):
        # Check if patient_id is in format "T<number>" or just a number
        if patient.patient_id.startswith('T'):
            # Update T-prefixed IDs to be sequential
            patient.patient_id = f"T{i}"
        else:
            # Update numeric IDs to be sequential
            try:
                # Try to convert to int to check if it's a pure number
                int(patient.patient_id)
                patient.patient_id = str(i)
            except ValueError:
                # If it's not a pure number, keep as is but log
                pass
    db.session.commit()

@main.route('/patients', methods=['GET', 'POST'])
@role_required('supervisor')
def manage_patients():
    if request.method == 'POST':
        # Handle file upload
        if 'csv_file' in request.files and request.files['csv_file'].filename != '':
            file = request.files['csv_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                if filename.endswith('.csv'):
                    # Process CSV upload
                    stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
                    csv_input = csv.reader(stream)
                    
                    # Skip header row
                    next(csv_input, None)
                    
                    added_count = 0
                    skipped_count = 0
                    
                    for row in csv_input:
                        # Handle different CSV formats:
                        # Format 1 (Simple): ID, Name, Actual Age, Sex (4 columns)
                        # Format 2 (Full): ID, Name, Age, Sex, OPG, A code, D code, A Age, D Age, Actual age (10+ columns)
                        
                        patient_id = ''
                        name = ''
                        actual_age = ''
                        sex = ''
                        code_a = ''
                        code_b = ''
                        
                        if len(row) >= 4:  # Simple format
                            patient_id = row[0]
                            name = row[1]
                            actual_age = row[2]
                            sex = row[3]
                            
                            # Check if it's the full format (10+ columns)
                            if len(row) >= 10:
                                # Override with full format data
                                patient_id = row[0]
                                name = row[1]
                                actual_age = row[9]
                                sex = row[3]
                                code_a = row[5]
                                code_b = row[6]
                            
                            # Check if patient already exists
                            patient = Patient.query.filter_by(patient_id=patient_id).first()
                            if not patient:
                                patient = Patient(
                                    patient_id=patient_id,
                                    name=name,
                                    actual_age=float(actual_age) if actual_age else 0,
                                    sex=sex,
                                    code_a=code_a if code_a else None,
                                    code_b=code_b if code_b else None
                                )
                                db.session.add(patient)
                                added_count += 1
                                # Commit in batches to handle large datasets
                                if added_count % 100 == 0:
                                    db.session.flush()
                            else:
                                skipped_count += 1
                    
                    try:
                        db.session.commit()
                        flash(f'CSV import successful! Added: {added_count}, Skipped (already exist): {skipped_count}')
                    except Exception as e:
                        db.session.rollback()
                        flash(f'Error importing CSV: {str(e)}')
                        
                else:  # Excel file
                    # Process Excel upload
                    try:
                        # Save file to a temporary location to process with openpyxl
                        file.stream.seek(0)
                        temp_file_path = os.path.join('/tmp', file.filename)
                        file.save(temp_file_path)
                        
                        # Load workbook
                        workbook = openpyxl.load_workbook(temp_file_path, data_only=True)
                        worksheet = workbook.active
                        
                        # Skip header row
                        first_row = True
                        row_count = 0
                        added_count = 0
                        skipped_count = 0
                        
                        for row in worksheet.iter_rows(values_only=True):
                            if first_row:
                                first_row = False
                                continue
                            
                            row_count += 1
                            # Handle different Excel formats:
                            # Format 1 (Simple): ID, Name, Actual Age, Sex (4 columns)
                            # Format 2 (Full): ID, Name, Age, Sex, OPG, A code, D code, A Age, D Age, Actual age (10+ columns)
                            
                            patient_id = ''
                            name = ''
                            actual_age = ''
                            sex = ''
                            code_a = ''
                            code_b = ''
                            
                            if len(row) >= 4:  # Simple format
                                patient_id = str(row[0]) if row[0] else ''
                                name = str(row[1]) if row[1] else ''
                                actual_age = str(row[2]) if row[2] else ''
                                sex = str(row[3]) if row[3] else ''
                                
                                # Check if it's the full format (10+ columns)
                                if len(row) >= 10:
                                    # Override with full format data
                                    patient_id = str(row[0]) if row[0] else ''
                                    name = str(row[1]) if row[1] else ''
                                    actual_age = str(row[9]) if row[9] else ''  # Column 9 is actual age
                                    sex = str(row[3]) if row[3] else ''  # Column 3 is sex
                                    code_a = str(row[5]) if row[5] else ''  # Column 5 is A code
                                    code_b = str(row[6]) if row[6] else ''  # Column 6 is D code
                                
                                # Check if we have a patient_id
                                if patient_id:
                                    # Check if patient already exists
                                    patient = Patient.query.filter_by(patient_id=patient_id).first()
                                    if not patient:
                                        patient = Patient(
                                            patient_id=patient_id,
                                            name=name,
                                            actual_age=float(actual_age) if actual_age and actual_age.replace('.', '', 1).isdigit() else 0,
                                            sex=sex,
                                            code_a=code_a if code_a else None,  # Ensure None if empty
                                            code_b=code_b if code_b else None   # Ensure None if empty
                                        )
                                        db.session.add(patient)
                                        added_count += 1
                                        # Commit in batches to handle large datasets
                                        if added_count % 100 == 0:
                                            db.session.flush()
                                    else:
                                        skipped_count += 1
                        
                        workbook.close()
                        # Clean up temp file
                        os.remove(temp_file_path)
                        
                        try:
                            db.session.commit()
                            flash(f'Excel import successful! Added: {added_count}, Skipped (already exist): {skipped_count}')
                        except Exception as e:
                            db.session.rollback()
                            flash(f'Error importing Excel: {str(e)}')
                    except Exception as e:
                        # Clean up temp file on error
                        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                            os.remove(temp_file_path)
                        flash(f'Error processing Excel file: {str(e)}')
                        
        else:
            # Handle manual patient creation
            patient_id = request.form['patient_id']
            name = request.form.get('name', '')
            actual_age = float(request.form['actual_age'])
            sex = request.form['sex']
            
            # Check if patient already exists
            patient = Patient.query.filter_by(patient_id=patient_id).first()
            if not patient:
                patient = Patient(
                    patient_id=patient_id,
                    name=name,
                    actual_age=actual_age,
                    sex=sex
                )
                db.session.add(patient)
                try:
                    db.session.commit()
                    flash('Patient added successfully!')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error adding patient: {str(e)}')
            else:
                flash('Patient with this ID already exists!')
        
        # Renumber patient IDs after any addition
        renumber_patient_ids()
        
        return redirect(url_for('main.manage_patients'))
    
    # Handle search functionality and pagination
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Show 20 entries per page
    
    # Query patients with search and pagination
    patients_query = Patient.query
    
    if search_query:
        patients_query = patients_query.filter(
            db.or_(
                Patient.patient_id.contains(search_query),
                Patient.name.contains(search_query),
                Patient.code_a.contains(search_query),
                Patient.code_b.contains(search_query)
            )
        )
    
    # Order patients by patient_id numerically
    patients_query = patients_query.order_by(cast(Patient.patient_id, db.Integer))
    
    # Get patients with pagination
    patients = patients_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the content part for AJAX requests
        return render_template('patients_content.html', patients=patients, search_query=search_query)
    
    return render_template('patients.html', patients=patients, search_query=search_query)

@main.route('/patients/update/<int:id>', methods=['GET', 'POST'])
@role_required('supervisor')
def update_patient(id):
    patient = Patient.query.get_or_404(id)
    
    if request.method == 'POST':
        old_patient_id = patient.patient_id
        
        # Update patient details
        patient.patient_id = request.form['patient_id']
        patient.name = request.form.get('name', '')
        patient.actual_age = float(request.form['actual_age'])
        patient.sex = request.form['sex']
        
        try:
            db.session.commit()
            flash('Patient updated successfully!')
            
            # If patient_id was changed, renumber all patient IDs
            if old_patient_id != patient.patient_id:
                renumber_patient_ids()
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating patient: {str(e)}')
        
        return redirect(url_for('main.manage_patients'))
    
    return render_template('update_patient.html', patient=patient)

@main.route('/patients/delete/<int:patient_id>', methods=['POST'])
@role_required('supervisor')
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Delete OPG image file if it exists
    if patient.opg_link:
        try:
            os.remove(os.path.join(current_app.root_path, patient.opg_link))
        except:
            pass  # If file doesn't exist or can't be deleted, continue anyway
    
    # Delete the patient record
    db.session.delete(patient)
    
    try:
        db.session.commit()
        flash('Patient deleted successfully!')
        
        # Renumber patient IDs after deletion
        renumber_patient_ids()
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting patient: {str(e)}')
    
    return redirect(url_for('main.manage_patients'))

@main.route('/assign_codes')
@role_required('supervisor')
def assign_codes():
    patients = Patient.query.filter((Patient.code_a.is_(None)) | (Patient.code_b.is_(None))).all()
    
    for patient in patients:
        if not patient.code_a:
            # Generate random code for AlQahtani method
            patient.code_a = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        if not patient.code_b:
            # Generate random code for Demirjian method
            patient.code_b = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    db.session.commit()
    flash('Codes assigned to all patients')
    return redirect(url_for('main.manage_patients'))

@main.route('/upload_opg/<int:patient_id>', methods=['GET', 'POST'])
@role_required('supervisor')
def upload_opg(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        # Handle file upload
        if 'opg_file' in request.files:
            file = request.files['opg_file']
            if file and allowed_file(file.filename):
                # Create upload directory if it doesn't exist
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                
                filename = secure_filename(f"{patient.patient_id}_{file.filename}")
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                # Store relative path in database
                patient.opg_link = f"/{UPLOAD_FOLDER}/{filename}"
                db.session.commit()
                flash('OPG uploaded successfully')
                return redirect(url_for('main.manage_patients'))
    
    return render_template('upload_opg.html', patient=patient)

# Serve uploaded files
@main.route('/uploads/<filename>')
def uploaded_file(filename):
    # Only allow access to authenticated users
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Return the file from the uploads directory
    return send_from_directory(UPLOAD_FOLDER, filename)

@main.route('/blinded_data')
@role_required('supervisor')
def blinded_data():
    # Handle search functionality and pagination
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Show 20 entries per page
    
    # Generate blinded data for PI
    patients_query = Patient.query.filter(
        db.or_(
            Patient.code_a.isnot(None), 
            Patient.code_b.isnot(None)
        )
    )
    
    if search_query:
        patients_query = patients_query.filter(
            db.or_(
                Patient.code_a.contains(search_query),
                Patient.code_b.contains(search_query)
            )
        )
    
    # Get patients with pagination
    patients = patients_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    blinded_entries = []
    for patient in patients.items:
        # Add AlQahtani entry if code exists
        if patient.code_a:
            entry_a = {
                'code': patient.code_a,
                'opg_link': patient.opg_link,
                'sex': patient.sex,
                'method': 'AlQahtani'
            }
            blinded_entries.append(entry_a)
        
        # Add Demirjian entry if code exists
        if patient.code_b:
            entry_b = {
                'code': patient.code_b,
                'opg_link': patient.opg_link,
                'sex': patient.sex,
                'method': 'Demirjian'
            }
            blinded_entries.append(entry_b)
    
    # Shuffle the data
    random.shuffle(blinded_entries)
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the content part for AJAX requests
        return render_template('blinded_data_content.html', entries=blinded_entries, search_query=search_query, patients=patients)
    
    return render_template('blinded_data.html', entries=blinded_entries, search_query=search_query, patients=patients)

@main.route('/estimate_age', methods=['GET', 'POST'])
@role_required('pi')
def estimate_age():
    if request.method == 'POST':
        # Validate CSRF token
        if not validate_csrf_token():
            flash('Security token validation failed. Please try again.')
            return redirect(url_for('main.estimate_age'))
            
        code = request.form['code']
        estimated_age = float(request.form['estimated_age'])
        method = request.form['method']
        
        # Create estimation entry
        estimation = EstimationEntry(
            code=code,
            estimated_age=estimated_age,
            method_used=method
        )
        
        # Note: We're no longer collecting individual tooth stage data
        # The PI only provides the final estimated age
        
        db.session.add(estimation)
        db.session.commit()
        
        # Update patient record with estimated age
        patient = Patient.query.filter(
            (Patient.code_a == code) | (Patient.code_b == code)
        ).first()
        
        if patient:
            if code == patient.code_a:
                patient.alqahtani_estimated_age = estimated_age
            elif code == patient.code_b:
                patient.demirjian_estimated_age = estimated_age
        
        db.session.commit()
        
        flash('Estimation submitted successfully')
        return redirect(url_for('main.estimate_age'))
    
    # Handle search functionality and pagination
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Show 20 entries per page
    
    # Show blinded data for the PI to work with
    # Get all patients that have codes assigned but not yet estimated
    patients_query = Patient.query.filter(
        Patient.code_a.isnot(None), 
        Patient.code_b.isnot(None)
    )
    
    if search_query:
        patients_query = patients_query.filter(
            db.or_(
                Patient.code_a.contains(search_query),
                Patient.code_b.contains(search_query)
            )
        )
    
    # Apply pagination
    patients = patients_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Find which codes have already been estimated
    existing_estimations = EstimationEntry.query.with_entities(EstimationEntry.code).all()
    estimated_codes = [e.code for e in existing_estimations]
    
    # Prepare blinded entries that haven't been estimated yet
    blinded_entries = []
    for patient in patients.items:
        # Add AlQahtani entry if code exists and not estimated yet
        if patient.code_a and patient.code_a not in estimated_codes:
            entry = {
                'code': patient.code_a,
                'opg_link': patient.opg_link,
                'sex': patient.sex,
                'method': 'AlQahtani'
            }
            blinded_entries.append(entry)
        
        # Add Demirjian entry if code exists and not estimated yet
        if patient.code_b and patient.code_b not in estimated_codes:
            entry = {
                'code': patient.code_b,
                'opg_link': patient.opg_link,
                'sex': patient.sex,
                'method': 'Demirjian'
            }
            blinded_entries.append(entry)
    
    # Shuffle the data
    random.shuffle(blinded_entries)
    
    # Remove the artificial limit that was causing issues
    # The pagination will handle the appropriate number of entries to display
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the content part for AJAX requests
        return render_template('estimate_age_content.html', entries=blinded_entries, search_query=search_query, patients=patients)
    
    return render_template('estimate_age.html', entries=blinded_entries, search_query=search_query, patients=patients)

@main.route('/get_estimation_form')
@role_required('pi')
def get_estimation_form():
    code = request.args.get('code')
    method = request.args.get('method')
    opg = request.args.get('opg')
    sex = request.args.get('sex')
    
    # Get teeth based on method
    if method == 'AlQahtani':
        teeth = get_alqahtani_teeth()
    else:  # Demirjian
        teeth = get_demirjian_teeth()
    
    return render_template('estimation_form.html', 
                          code=code, 
                          method=method, 
                          opg=opg, 
                          sex=sex, 
                          teeth=teeth)

@main.route('/analysis')
@role_required('supervisor')
def analysis():
    # Handle search functionality and pagination
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Show 20 patients per page
    
    # Get all patients and their estimations
    if search_query:
        patients_query = Patient.query.filter(
            db.or_(
                Patient.patient_id.contains(search_query),
                Patient.name.contains(search_query),
                Patient.code_a.contains(search_query),
                Patient.code_b.contains(search_query)
            )
        )
    else:
        patients_query = Patient.query
    
    # Apply pagination
    patients = patients_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    results = []
    alqahtani_data = []
    demirjian_data = []
    
    for patient in patients.items:
        result = {
            'patient_id': patient.patient_id,
            'name': patient.name,
            'actual_age': patient.actual_age,
            'sex': patient.sex,
            'opg_link': patient.opg_link,
            'code_a': patient.code_a,
            'code_b': patient.code_b,
            'alqahtani_estimated': patient.alqahtani_estimated_age or 'Not estimated',
            'demirjian_estimated': patient.demirjian_estimated_age or 'Not estimated'
        }
        
        results.append(result)
        
        # Collect data for visualization
        if patient.alqahtani_estimated_age:
            alqahtani_data.append((patient.actual_age, patient.alqahtani_estimated_age))
        
        if patient.demirjian_estimated_age:
            demirjian_data.append((patient.actual_age, patient.demirjian_estimated_age))
    
    # Generate accuracy comparison chart
    accuracy_chart = None
    if alqahtani_data or demirjian_data:
        accuracy_chart = generate_accuracy_chart(alqahtani_data, demirjian_data)
    
    # Generate method comparison chart
    comparison_chart = None
    if alqahtani_data or demirjian_data:
        comparison_chart = generate_method_comparison_chart(alqahtani_data, demirjian_data)
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return only the content part for AJAX requests
        return render_template('analysis_content.html', 
                              results=results,
                              accuracy_chart=accuracy_chart,
                              comparison_chart=comparison_chart,
                              search_query=search_query,
                              patients=patients)
    
    return render_template('analysis.html', 
                          results=results,
                          accuracy_chart=accuracy_chart,
                          comparison_chart=comparison_chart,
                          search_query=search_query,
                          patients=patients)

def generate_accuracy_chart(alqahtani_data, demirjian_data):
    """Generate a scatter plot comparing estimated vs actual ages"""
    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot AlQahtani data
    if alqahtani_data:
        alq_actual, alq_estimated = zip(*alqahtani_data)
        ax.scatter(alq_actual, alq_estimated, label='AlQahtani Method', alpha=0.7, s=60)
    
    # Plot Demirjian data
    if demirjian_data:
        dem_actual, dem_estimated = zip(*demirjian_data)
        ax.scatter(dem_actual, dem_estimated, label='Demirjian Method', alpha=0.7, s=60)
    
    # Plot ideal line (where estimated = actual)
    all_actual = [age for age, _ in alqahtani_data] + [age for age, _ in demirjian_data]
    if all_actual:
        min_age, max_age = min(all_actual), max(all_actual)
        ax.plot([min_age, max_age], [min_age, max_age], 'r--', label='Perfect Estimation', linewidth=2)
    
    ax.set_xlabel('Actual Age (years)')
    ax.set_ylabel('Estimated Age (years)')
    ax.set_title('Estimated vs Actual Age Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Save plot to base64 string
    img = BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    
    return plot_url

def generate_method_comparison_chart(alqahtani_data, demirjian_data):
    """Generate a bar chart comparing the accuracy of both methods"""
    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Calculate mean absolute errors
    alq_mae = 0
    dem_mae = 0
    
    if alqahtani_data:
        alq_mae = np.mean([abs(actual - estimated) for actual, estimated in alqahtani_data])
    
    if demirjian_data:
        dem_mae = np.mean([abs(actual - estimated) for actual, estimated in demirjian_data])
    
    # Create bar chart
    methods = ['AlQahtani', 'Demirjian']
    maes = [alq_mae, dem_mae]
    
    bars = ax.bar(methods, maes, color=['#1f77b4', '#ff7f0e'], alpha=0.7, edgecolor='black')
    
    # Add value labels on bars
    for bar, mae in zip(bars, maes):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{mae:.2f}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel('Mean Absolute Error (years)')
    ax.set_title('Method Comparison - Mean Absolute Error')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Save plot to base64 string
    img = BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    
    return plot_url

@main.route('/export_patients')
@role_required('supervisor')
def export_patients():
    # Export all patients as Excel file with embedded images
    # Process in batches to handle large datasets
    
    # Create a workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Patient Data"
    
    # Write header
    headers = ['ID', 'Name', 'Age', 'Sex', 'OPG Image', 'A code', 'D code', 'A Age', 'D Age', 'Actual age']
    ws.append(headers)
    
    # Set column widths
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 15
    
    # Make header row bold
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = cell.font.copy(bold=True)
    
    # Process patients in batches to handle large datasets
    offset = 0
    batch_size = 100
    has_more = True
    
    while has_more:
        patients = Patient.query.offset(offset).limit(batch_size).all()
        if not patients:
            has_more = False
            continue
            
        # Write data
        for row_idx, patient in enumerate(patients, start=offset+2):
            # Add patient data
            ws.cell(row=row_idx, column=1, value=patient.patient_id)
            ws.cell(row=row_idx, column=2, value=patient.name)
            ws.cell(row=row_idx, column=3, value=patient.actual_age)
            ws.cell(row=row_idx, column=4, value=patient.sex)
            # Image column (5) will be handled separately
            ws.cell(row=row_idx, column=6, value=patient.code_a)
            ws.cell(row=row_idx, column=7, value=patient.code_b)
            ws.cell(row=row_idx, column=8, value=patient.alqahtani_estimated_age)
            ws.cell(row=row_idx, column=9, value=patient.demirjian_estimated_age)
            ws.cell(row=row_idx, column=10, value=patient.actual_age)
            
            # Handle image embedding if image exists
            if patient.opg_link:
                # Extract filename from the path
                image_path = patient.opg_link.lstrip('/')
                if os.path.exists(image_path):
                    try:
                        # Load and resize image
                        img = ExcelImage(image_path)
                        # Resize image to fit in the cell
                        img.width = 100
                        img.height = 100
                        
                        # Add image to the worksheet
                        ws.add_image(img, f'E{row_idx}')
                    except Exception as e:
                        # If there's an error loading the image, put error message in the cell
                        ws.cell(row=row_idx, column=5, value=f"Error loading image: {str(e)}")
                else:
                    # If image file doesn't exist, put a note in the cell
                    ws.cell(row=row_idx, column=5, value="Image not found")
        
        offset += len(patients)
        if len(patients) < batch_size:
            has_more = False
    
    # Save the workbook to a BytesIO buffer
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=patients.xlsx"}
    )