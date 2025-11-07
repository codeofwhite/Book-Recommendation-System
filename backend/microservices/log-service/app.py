# log_service/app.py
from flask import Flask
from flask_cors import CORS
import os # Import os to get environment variables

# Import the blueprint from the routes module
from routes.log_routes import log_bp

app = Flask(__name__)
CORS(app) # Enable CORS for all origins, or configure it more restrictively as needed

# Register the blueprint
app.register_blueprint(log_bp)

if __name__ == '__main__':
    # Get port from environment variable, default to 5006
    port = int(os.environ.get('PORT', 5006))
    # Get debug mode from environment variable, default to True for development
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"Log Service starting on http://0.0.0.0:{port} (Debug: {debug_mode})")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)