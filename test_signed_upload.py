import os
from supabase import create_client

def test():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)
    
    # Check if create_signed_upload_url exists
    print("Methods on from_('opg-images'):")
    print(dir(supabase.storage.from_('opg-images')))
    
    try:
        res = supabase.storage.from_('opg-images').create_signed_upload_url('test_path.xlsx')
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test()
