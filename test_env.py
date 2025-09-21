import os

def test_environment():
    print("Environment Variables:")
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'not set')}")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'not set')}")
    print(f"SECRET_KEY: {'set' if os.environ.get('SECRET_KEY') else 'not set'}")
    print(f"SUPABASE_URL: {os.environ.get('SUPABASE_URL', 'not set')}")
    print(f"SUPABASE_KEY: {'set' if os.environ.get('SUPABASE_KEY') else 'not set'}")

if __name__ == "__main__":
    test_environment()