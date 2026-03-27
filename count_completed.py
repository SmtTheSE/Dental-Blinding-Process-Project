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
    completed = [p for p in patients if p.get('alqahtani_estimated_age') is not None and p.get('demirjian_estimated_age') is not None]
    pending = [p for p in patients if p.get('alqahtani_estimated_age') is None or p.get('demirjian_estimated_age') is None]
    
    # In PI view, each pending patient generates up to 2 tasks (AlQ, Dem)
    pending_tasks = 0
    for p in pending:
        if p.get('alqahtani_estimated_age') is None: pending_tasks += 1
        if p.get('demirjian_estimated_age') is None: pending_tasks += 1

    print(f"Total fully completed patients: {len(completed)}")
    print(f"Total pending patients: {len(pending)}")
    print(f"Total pending tasks: {pending_tasks}")
    print(f"Total patients displayed to PI (pending patients + min(completed, 10)): {len(pending) + min(len(completed), 10)}")
    print(f"What if they count 'codes' instead of patients?")
