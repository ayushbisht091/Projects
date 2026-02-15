from flask import Flask, jsonify
from flask_cors import CORS
from auth import auth_bp
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Flask Session Cookie Configuration for local development
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False # Essential for HTTP development

# Configure CORS for the entire application
CORS_ORIGINS = ["http://localhost:5000", "http://127.0.0.1:5500", "http://127.0.0.1:5000"]
CORS(app, resources={r"/*": {"origins": CORS_ORIGINS}}, supports_credentials=True)

# Log the configured CORS origins for debugging
logger.info(f"Configured CORS origins: {CORS_ORIGINS}")

# Register blueprints
app.register_blueprint(auth_bp)

# Create database directory if it doesn't exist
os.makedirs('database', exist_ok=True)

@app.route('/')
def home():
    return jsonify({"status": "Server is running"})

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    try:
        logger.info("Starting server on http://127.0.0.1:5000")
        app.run(host='127.0.0.1', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise 
    