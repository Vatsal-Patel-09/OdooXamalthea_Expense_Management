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

# Import routes
from routes.auth import auth_bp
from routes.users import users_bp
from routes.categories import categories_bp
from routes.expenses import expenses_bp
from routes.approvals import approvals_bp

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# CORS Configuration - Allow frontend
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": [FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(categories_bp, url_prefix='/api/categories')
app.register_blueprint(expenses_bp, url_prefix='/api/expenses')
app.register_blueprint(approvals_bp, url_prefix='/api/approvals')

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
