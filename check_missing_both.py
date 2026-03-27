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
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

patients = fetch(f"{supabase_url}/rest/v1/patient?select=*")
if patients:
    both_missing = [p for p in patients if p.get('alqahtani_estimated_age') is None and p.get('demirjian_estimated_age') is None]
    some_missing = [p for p in patients if (p.get('alqahtani_estimated_age') is None) != (p.get('demirjian_estimated_age') is None)]
    
    print(f"Patients with BOTH missing: {len(both_missing)}")
    print(f"Patients with ONE missing: {len(some_missing)}")
