import urllib.request
import json

supabase_url = "https://hlxacefixdrvljnxqaaq.supabase.co"
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhseGFjZWZpeGRydmxqbnhxYWFxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDA5MDA4NywiZXhwIjoyMDg1NjY2MDg3fQ.b0j1AOiIkYUv-fK135DOSiwmD6XGqPeggb07AByUKqY"

headers = {
    "apikey": jwt_token,
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

patients = fetch(f"{supabase_url}/rest/v1/patient?select=*")
entries = fetch(f"{supabase_url}/rest/v1/estimation_entry?select=*")

if patients and entries:
    entry_codes = set(e['code'] for e in entries)
    
    # Count how many patients have both codes in entries
    both_in = [p for p in patients if p.get('code_a') in entry_codes and p.get('code_b') in entry_codes]
    # Count how many patients have at least one code in entries
    any_in = [p for p in patients if p.get('code_a') in entry_codes or p.get('code_b') in entry_codes]
    
    print(f"Patients with BOTH codes in EstimationEntry: {len(both_in)}")
    print(f"Patients with AT LEAST ONE code in EstimationEntry: {len(any_in)}")
    
    # Count how many unique codes in patients vs entries
    patient_codes = set()
    for p in patients:
        if p.get('code_a'): patient_codes.add(p.get('code_a'))
        if p.get('code_b'): patient_codes.add(p.get('code_b'))
        
    print(f"Total unique codes assigned to patients: {len(patient_codes)}")
    
    # Check if there are codes that ARE in entries but NOT assigned to any patient!
    orphan_codes = set(c for c in entry_codes if c not in patient_codes)
    print(f"Estimation entries with orphaned codes: {len(orphan_codes)}")
    
    # Check if any patients DO NOT have code_a or code_b assigned
    missing_codes = [p for p in patients if not p.get('code_a') or not p.get('code_b')]
    print(f"Patients missing either code_a or code_b in DB: {len(missing_codes)}")
