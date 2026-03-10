#!/usr/bin/env python3
"""
Chrome simulation test - mimicking exactly how Chrome handles downloads
"""
import sys
import os
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simulate_chrome_download():
    """Simulate Chrome's exact download behavior"""
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    # Chrome's User-Agent string
    chrome_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1'
    }
    
    print("🦊 SIMULATING CHROME DOWNLOAD BEHAVIOR")
    print("=" * 50)
    
    try:
        # Login with Chrome headers
        print("1. Login with Chrome headers...")
        response = session.get(base_url + "/login", headers=chrome_headers)
        csrf_token = response.text.split('name="csrf_token" value="')[1].split('"')[0]
        
        login_data = {
            'username': 'supervisor',
            'password': 'supervisor',
            'csrf_token': csrf_token
        }
        response = session.post(base_url + "/login", data=login_data, headers=chrome_headers, allow_redirects=True)
        print(f"   Login successful: {response.status_code}")
        
        # Chrome typically does a HEAD request first
        print("\n2. Chrome HEAD request (preflight)...")
        head_response = session.head(base_url + "/export_patients", headers=chrome_headers)
        print(f"   HEAD Status: {head_response.status_code}")
        for key, value in head_response.headers.items():
            if 'content' in key.lower():
                print(f"   {key}: {value}")
        
        # Then the actual GET request
        print("\n3. Chrome GET request...")
        get_response = session.get(base_url + "/export_patients", headers=chrome_headers, stream=True)
        print(f"   GET Status: {get_response.status_code}")
        
        # Analyze the response
        content = get_response.content
        print(f"   Content Length: {len(content)} bytes")
        print(f"   Magic Bytes: {content[:4].hex()}")
        
        if content[:4] == b'PK\x03\x04':
            print("   ✅ Valid Excel file received")
            
            # Save with Chrome-like filename
            filename = "chrome_simulation_export.xlsx"
            with open(filename, 'wb') as f:
                f.write(content)
            print(f"   File saved: {filename}")
            
            return True
        else:
            print("   ❌ Invalid content received")
            print(f"   Content preview: {content[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simulate_chrome_download()
    if success:
        print("\n🎉 Chrome simulation successful")
        sys.exit(0)
    else:
        print("\n❌ Chrome simulation failed")
        sys.exit(1)