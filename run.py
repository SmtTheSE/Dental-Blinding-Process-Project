from app import create_app
import os

# Use production config by default, but allow override via FLASK_ENV
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)