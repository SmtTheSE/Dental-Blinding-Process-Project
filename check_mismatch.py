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
    print(f"Total entries: {len(entries)}")
    entry_codes = set(e['code'] for e in entries)
    
    missing_patients = []
    
    for p in patients:
        a = p.get('code_a')
        b = p.get('code_b')
        
        a_is_estimated = a in entry_codes
        b_is_estimated = b in entry_codes
        
        a_is_saved = p.get('alqahtani_estimated_age') is not None
        b_is_saved = p.get('demirjian_estimated_age') is not None
        
        if (a_is_estimated and not a_is_saved) or (b_is_estimated and not b_is_saved):
            print(f"Mismatch for Patient {p.get('patient_id')}:")
            if a_is_estimated and not a_is_saved:
                print(f"  Code A ({a}) has EstimationEntry but Patient row AlQahtani is None!")
            if b_is_estimated and not b_is_saved:
                print(f"  Code B ({b}) has EstimationEntry but Patient row Demirjian is None!")
                
    # Also track "Fully vanished" patients
    # They have BOTH codes estimated (or at least one but both are not pending/completed)
    for p in patients:
        a = p.get('code_a')
        b = p.get('code_b')
        if (a in entry_codes and p.get('alqahtani_estimated_age') is None) or \
           (b in entry_codes and p.get('demirjian_estimated_age') is None):
            print(f"==> Patient {p.get('patient_id')} is partially/fully vanished.")
