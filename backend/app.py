"""
Main Flask Application Entry Point
Flask backend with Supabase integration for Expense Management System
"""

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables FIRST before importing anything else
backend_dir = Path(__file__).resolve().parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

# Import database config AFTER loading env
from config.database import test_connection

# Import route blueprints
from routes.auth import auth_bp
from routes.users import users_bp
from routes.countries import countries_bp
from routes.categories import categories_bp
from routes.upload import upload_bp
from routes.expenses import expenses_bp

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

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(countries_bp, url_prefix='/api')
app.register_blueprint(categories_bp, url_prefix='/api/categories')
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(expenses_bp, url_prefix='/api/expenses')

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
