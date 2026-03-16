# Dental Age Estimation System - Testing Guide

This guide provides step-by-step instructions for testing the dental age estimation system with sample data and role-specific workflows.

## Sample Data for Testing

### Sample Patient Records

| ID  | Name           | Age | Sex | Actual Age |
|-----|----------------|-----|-----|------------|
| T01 | John Smith     | 12  | M   | 12.5       |
| T02 | Emily Johnson  | 14  | F   | 14.2       |
| T03 | Michael Brown  | 10  | M   | 10.8       |
| T04 | Sarah Davis    | 16  | F   | 15.9       |
| T05 | David Wilson   | 13  | M   | 13.1       |

### Sample OPG Image Files
For testing purposes, you can use any image files with the following names:
- T01_opg.jpg
- T02_opg.jpg
- T03_opg.jpg
- T04_opg.jpg
- T05_opg.jpg

## Role Testing Guidelines

### Supervisor Testing Workflow

#### 1. Login as Supervisor
- Username: `supervisor`
- Password: `supervisor`

#### 2. Add Sample Patients
1. Navigate to "Manage Patients" from the dashboard
2. Add patients manually using the form:
   - Patient ID: T01
   - Name: John Smith
   - Actual Age: 12.5
   - Sex: M
   - Click "Add Patient"
3. Repeat for all sample patients (T02-T05)

#### 3. Batch Import via CSV (Alternative Method)
1. Create a CSV file with the following content:
   ```csv
   ID,Name,Age,Sex,OPG,A code,D code,A Age,D Age,Actual age
   T01,John Smith,12,M,,,,"","",12.5
   T02,Emily Johnson,14,F,,,,"","",14.2
   T03,Michael Brown,10,M,,,,"","",10.8
   T04,Sarah Davis,16,F,,,,"","",15.9
   T05,David Wilson,13,M,,,,"","",13.1
   ```
2. Navigate to "Manage Patients"
3. Click "Upload CSV" and select your file
4. Verify patients are imported correctly

#### 4. Assign Codes
1. Navigate to "Assign Codes" from the dashboard
2. Click "Assign Codes to All Patients"
3. Verify that each patient now has unique A and D codes

#### 5. Upload OPG Images
1. Navigate to "Manage Patients"
2. For each patient, click "Upload OPG"
3. Select the corresponding image file
4. Verify images are uploaded and linked to patients

#### 6. View Blinded Data
1. Navigate to "Blinded Data" from the dashboard
2. Verify that data is properly blinded (only codes, OPG images, and sex visible)
3. Note that data is shuffled to prevent method identification

#### 7. Perform Analysis
1. After PI completes estimations, navigate to "Analysis"
2. Review the comparison between actual ages and estimated ages
3. Verify accuracy metrics are displayed

### Principal Investigator (PI) Testing Workflow

#### 1. Login as PI
- Username: `pi`
- Password: `pi`

#### 2. Perform Age Estimations
1. Navigate to "Estimate Age" from the dashboard
2. For each blinded entry:
   - View the OPG image and sex
   - Select the appropriate method (AlQahtani or Demirjian)
   - Enter the estimated age
   - Fill in tooth development stages as required
   - Submit the estimation
3. Repeat for all blinded entries

#### 3. Verify Completed Estimations
1. Navigate to "Estimate Age" again
2. Confirm that previously estimated entries are no longer shown
3. Only new entries should be available for estimation

## Data Insertion Guidelines

### Manual Data Entry

#### For Supervisors:
1. Go to "Manage Patients"
2. Fill in all required fields:
   - Patient ID (unique identifier)
   - Name (participant's full name)
   - Actual Age (chronological age in years)
   - Sex (M/F)
3. Click "Add Patient"

### Batch Data Import

#### For Supervisors:
1. Prepare a CSV file with the following columns:
   - ID: Participant identifier
   - Name: Participant's full name
   - Age: Age as recorded
   - Sex: Participant's sex (M/F)
   - OPG: (optional) Path to OPG image
   - A code: (optional) Pre-assigned AlQahtani code
   - D code: (optional) Pre-assigned Demirjian code
   - A Age: (optional) Pre-recorded AlQahtani estimation
   - D Age: (optional) Pre-recorded Demirjian estimation
   - Actual age: Chronological age of participant
2. Go to "Manage Patients"
3. Click "Upload CSV"
4. Select your prepared file
5. Verify successful import

### OPG Image Upload

#### For Supervisors:
1. Go to "Manage Patients"
2. Click "Upload OPG" next to the patient
3. Select an image file (JPG, PNG, GIF)
4. Click "Upload"
5. Verify the image is linked to the patient

## Testing Scenarios

### Scenario 1: Complete Workflow Test
1. Supervisor adds patients
2. Supervisor assigns codes
3. Supervisor uploads OPG images
4. PI performs all age estimations
5. Supervisor reviews analysis

### Scenario 2: Batch Import Test
1. Prepare CSV with 10+ patients
2. Import via batch upload
3. Verify all patients appear in the system
4. Assign codes to all patients
5. Verify codes are unique and properly assigned

### Scenario 3: Data Export Test
1. Supervisor exports patient data
2. Verify CSV contains all required columns
3. Verify data integrity in exported file

### Scenario 4: Access Control Test
1. Try to access supervisor-only pages as PI
2. Verify access is denied
3. Try to access PI pages as supervisor
4. Verify access is granted where appropriate

## Troubleshooting

### Common Issues:

1. **Login Problems**:
   - Ensure using correct credentials
   - Default supervisor: username `supervisor`, password `supervisor`
   - Default PI: username `pi`, password `pi`

2. **Database Connection Issues**:
   - Verify PostgreSQL is running
   - Check database configuration in `config.py`
   - Ensure `dental_scheduler` database exists

3. **File Upload Issues**:
   - Verify file formats are supported (JPG, PNG, GIF)
   - Check file size limits
   - Ensure upload directory has proper permissions

4. **Missing Data**:
   - Verify all required fields are filled
   - Check database for integrity
   - Ensure codes are assigned before PI estimation

## Verification Checklist

### After Supervisor Testing:
- [ ] Patients added successfully
- [ ] Codes assigned to all patients
- [ ] OPG images uploaded and linked
- [ ] Blinded data view accessible
- [ ] Analysis page shows proper data

### After PI Testing:
- [ ] All blinded entries estimated
- [ ] Tooth development stages recorded
- [ ] Estimated ages saved correctly
- [ ] No duplicate estimations possible

This testing guide ensures that all functionality of the dental age estimation system works as expected and meets the requirements of your dental research workflow.