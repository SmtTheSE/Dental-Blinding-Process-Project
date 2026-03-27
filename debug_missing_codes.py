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
if patients:
    print(f"Total patients: {len(patients)}")
    missing_codes = []
    for p in patients:
        a = p.get('code_a')
        b = p.get('code_b')
        if not a or not b:
            missing_codes.append(p)
            print(f"Patient {p.get('patient_id')} ({p.get('name')}) is missing codes! code_a={a}, code_b={b}")
    print(f"Total missing: {len(missing_codes)}")
