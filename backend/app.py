"""
Main Flask Application Entry Point
Flask backend with Supabase integration for Expense Management System
"""

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import database config
from config.database import test_connection

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Enable CORS for all routes
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Basic health check route
@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Flask Backend Server is running!',
        'version': '1.0.0'
    }), 200

@app.route('/api/health')
def health_check():
    """Detailed health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Expense Management API',
        'environment': os.getenv('FLASK_ENV', 'development')
    }), 200

@app.route('/api/database/test')
def test_database():
    """Test database connection"""
    result = test_connection()
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting Flask server on http://{host}:{port}")
    print(f"📝 Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    app.run(host=host, port=port, debug=debug)
