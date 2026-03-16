from app import create_app
import os

# Use production config by default, but allow override via FLASK_ENV
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    display_port = 5001
    print(f"Starting server on port {display_port}...")
    # Debug mode explicitly enabled for local development to bypass HTTPS requirement
    # Production uses gunicorn via Procfile, so this only affects local 'python run.py'
    app.run(debug=True, host='0.0.0.0', port=display_port)