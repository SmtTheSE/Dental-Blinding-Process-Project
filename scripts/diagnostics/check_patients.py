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
    for p in patients:
        # Check rows like Thun Myat Moe (14)
        if p.get('patient_id') in ['14', '15', '16', '17', '18', '19', '20']:
            print(f"Patient {p.get('patient_id')} - {p.get('name')}:")
            print(f"  code_a: {p.get('code_a')}, code_b: {p.get('code_b')}")
            print(f"  alqahtani_estimated_age: {p.get('alqahtani_estimated_age')}, demirjian: {p.get('demirjian_estimated_age')}")
