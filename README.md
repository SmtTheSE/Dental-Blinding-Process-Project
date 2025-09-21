# Dental Age Estimation Web App with Blinding Workflow

This is a web application designed for dental age estimation in children (5-12 years old) using OPG (panoramic dental X-ray) images. The app supports two scientific methods (AlQahtani and Demirjian) and implements a robust blinding workflow to ensure scientific rigor.

## Features

### User Roles
1. **Supervisor (S)**: 
   - Manages master sheet
   - Assigns codes
   - Shuffles data
   - Controls blinding
   - Performs final analysis

2. **Principal Investigator (PI)**:
   - Receives blinded data
   - Enters age estimations via web forms
   - Never sees actual age or method during estimation

### Blinding Workflow

1. **Setup (Supervisor Only)**
   - Create Master Sheet with: Patient ID, Actual Age, OPG file/link, Sex
   - PI has no access at this stage

2. **OPG Input (PI)**
   - PI uploads or identifies the OPG image

3. **Coding (Supervisor Only)**
   - For each OPG, assign two randomized codes:
     - Code A for AlQahtani method
     - Code B for Demirjian method
   - Store these codes in the Master Sheet

4. **Blinding (Supervisor Only)**
   - Shuffle coded data
   - Prepare Blinded Sheet with only: Code, OPG file/link, Sex
   - Share this with PI for age estimation

5. **Estimation (PI)**
   - PI views only Code, OPG, and Sex
   - For each code, performs dental age estimation
   - Enters estimated age for each code

6. **Debrief & Analysis (Supervisor Only)**
   - Supervisor unblinds data using Master Sheet
   - Compare PI's estimated ages to actual ages and method used
   - Analyze accuracy and reliability of each method

### Tooth Detection and Age Estimation Logic

#### AlQahtani Method
- Detects and annotates developmental stages for:
  - Permanent teeth: 21, 22, 23, 24, 25, 26, 27, 31, 32, 33, 34, 35, 36, 37
  - Primary teeth: 61, 62, 63, 64, 65, 71, 72, 73, 74, 75
- Uses modified Moorrees and Bengston's criteria with stages I-XIII for formation and i-viii for eruption and resorption

#### Demirjian Method
- Detects and annotates developmental stages for left mandibular permanent teeth:
  - 31, 32, 33, 34, 35, 36, 37
- Uses stages A-H (Demirjian criteria)
- Converts stages to scores using self-weighted score table
- Calculates total dental maturity score
- Converts score to age using conversion tables (different for males and females)

## Installation

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Set up PostgreSQL database:
   - Create a database named `dental_scheduler`
   - Update the database connection string in `config.py` if needed

3. Run the setup:
   ```
   python setup_db.py
   ```
   This will initialize the database with default users:
   - Supervisor: username `supervisor`, password will be displayed in console
   - PI: username `pi`, password will be displayed in console

4. Start the application:
   ```
   python app.py
   ```

## Production Deployment

This application is ready for production deployment on Render.com with the included configuration files:

- `render.yaml`: Defines the web service and database
- `runtime.txt`: Specifies the Python version
- `requirements.txt`: Lists all dependencies

### Environment Variables

For production deployment, you should set these environment variables:

- `SECRET_KEY`: A strong secret key for Flask sessions
- `DATABASE_URL`: PostgreSQL connection string (automatically provided by Render)
- `FLASK_ENV`: Set to `production`

### Default User Passwords

During the first run, the application will generate strong passwords for the default users and display them in the logs. You should change these passwords after first login.

## Usage

1. Visit `http://localhost:5000` and log in with:
   - Supervisor: username `supervisor`, password (generated during setup)
   - PI: username `pi`, password (generated during setup)

2. Supervisor workflow:
   - Add patients with their actual age and sex
   - Upload OPG images
   - Assign codes to patients
   - Generate blinded data for PI
   - Perform final analysis

3. PI workflow:
   - View blinded data (codes only)
   - Enter age estimations for each code
   - Submit estimations

## Technical Implementation

- **Frontend**: Flask templates
- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Export Formats**: Excel, CSV

## Scientific References

- AlQahtani, S. et al. (2010). London Atlas of Human Tooth Development
- Demirjian, A. et al. (1973). A new system of dental age assessment
- Modified Moorrees and Bengston's criteria for tooth development stages