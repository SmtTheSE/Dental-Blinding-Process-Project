import urllib.request
import json
import sys

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
    except urllib.error.URLError as e:
        print(f"Error fetching {url}: {e}")
        return None

try:
    patients = fetch(f"{supabase_url}/rest/v1/patient?select=*")
    if patients:
        print(f"Total patients: {len(patients)}")
        missing_opg = []
        for p in patients:
            if not p.get('opg_link'):
                missing_opg.append(p)
                print(f"Patient {p.get('patient_id')} is missing OPG link.")
        print(f"Total missing OPG: {len(missing_opg)}")
except Exception as ex:
    print(f"Exception: {ex}")
