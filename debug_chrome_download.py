#!/usr/bin/env python3
"""
Debug script to simulate Chrome's download behavior and capture exactly what the browser receives
"""
import sys
import os
import requests
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_chrome_download():
    """Simulate Chrome download and capture all details"""
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    print("🔍 DEBUGGING CHROME DOWNLOAD BEHAVIOR")
    print("=" * 50)
    
    try:
        # Step 1: Get login page
        print("1. Getting login page...")
        response = session.get(base_url + "/login")
        print(f"   Status: {response.status_code}")
        print(f"   Cookies set: {list(session.cookies.keys())}")
        
        # Extract CSRF token
        csrf_match = 'name="csrf_token" value="'
        if csrf_match in response.text:
            csrf_start = response.text.find(csrf_match) + len(csrf_match)
            csrf_end = response.text.find('"', csrf_start)
            csrf_token = response.text[csrf_start:csrf_end]
            print(f"   CSRF Token extracted: {csrf_token[:20]}...")
        else:
            print("   ❌ No CSRF token found!")
            return False
        
        # Step 2: Login
        print("\n2. Logging in...")
        login_data = {
            'username': 'supervisor',
            'password': 'supervisor',
            'csrf_token': csrf_token
        }
        response = session.post(base_url + "/login", data=login_data, allow_redirects=True)
        print(f"   Login status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        print(f"   Session cookies: {list(session.cookies.keys())}")
        
        # Step 3: Test HEAD request (what Chrome does first)
        print("\n3. Testing HEAD request (Chrome's pre-flight check)...")
        head_response = session.head(base_url + "/export_patients")
        print(f"   HEAD Status: {head_response.status_code}")
        print("   HEAD Headers:")
        for key, value in head_response.headers.items():
            if key.lower() in ['content-disposition', 'content-type', 'content-length']:
                print(f"     {key}: {value}")
        
        # Step 4: Actual download request
        print("\n4. Testing actual GET request...")
        get_response = session.get(base_url + "/export_patients", stream=True)
        print(f"   GET Status: {get_response.status_code}")
        print(f"   Content-Type: {get_response.headers.get('Content-Type')}")
        print(f"   Content-Disposition: {get_response.headers.get('Content-Disposition')}")
        print(f"   Content-Length: {get_response.headers.get('Content-Length')}")
        
        # Step 5: Analyze the actual content
        print("\n5. Analyzing response content...")
        content = get_response.content
        print(f"   Content length: {len(content)} bytes")
        print(f"   First 20 bytes (hex): {content[:20].hex()}")
        print(f"   Last 20 bytes (hex): {content[-20:].hex()}")
        
        # Check if it's a valid Excel file
        if len(content) > 4:
            magic = content[:4]
            print(f"   Magic bytes: {magic.hex()}")
            if magic == b'PK\x03\x04':
                print("   ✅ Valid Excel/ZIP format detected")
            else:
                print("   ❌ Invalid file format")
                # Show what we actually got
                try:
                    text_content = content.decode('utf-8', errors='ignore')[:200]
                    print(f"   Text preview: {repr(text_content)}")
                except:
                    print("   Content appears to be binary data")
        
        # Step 6: Save file for inspection
        filename = "chrome_debug_export.xlsx"
        with open(filename, 'wb') as f:
            f.write(content)
        print(f"\n6. File saved as: {filename} ({os.path.getsize(filename)} bytes)")
        
        # Step 7: Verify with system tools
        print("\n7. System verification:")
        os.system(f"file {filename}")
        os.system(f"ls -la {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_chrome_download()
    if success:
        print("\n🎉 Debug completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Debug failed")
        sys.exit(1)