"""
Authentication Routes
Handles user signup, login, and authentication
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from utils.jwt_helper import generate_token
from utils.validators import validate_email, validate_password, validate_role
import bcrypt
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user and company
    First user becomes admin and creates company
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe",
            "company_name": "Acme Corp",
            "currency": "USD" (optional)
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'company_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        name = data['name'].strip()
        company_name = data['company_name'].strip()
        currency = data.get('currency', 'USD')
        
        # Validate email
        if not validate_email(email):
            return jsonify({
                'status': 'error',
                'message': 'Invalid email format'
            }), 400
        
        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 400
        
        supabase = get_supabase_client()
        
        # Check if user already exists
        existing_user = supabase.table('users').select('*').eq('email', email).execute()
        if existing_user.data:
            return jsonify({
                'status': 'error',
                'message': 'User with this email already exists'
            }), 409
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create company first
        company_data = {
            'name': company_name,
            'currency': currency
        }
        
        company_result = supabase.table('companies').insert(company_data).execute()
        
        if not company_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create company'
            }), 500
        
        company_id = company_result.data[0]['id']
        
        # Update company with created_by after user is created
        # For now, we'll create the user first
        
        # Create user (first user is admin)
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'role': 'admin',  # First user is admin
            'company_id': company_id,
            'is_active': True
        }
        
        user_result = supabase.table('users').insert(user_data).execute()
        
        if not user_result.data:
            # Rollback company creation if user creation fails
            supabase.table('companies').delete().eq('id', company_id).execute()
            return jsonify({
                'status': 'error',
                'message': 'Failed to create user'
            }), 500
        
        user = user_result.data[0]
        
        # Update company with created_by
        supabase.table('companies').update({'created_by': user['id']}).eq('id', company_id).execute()
        
        # Generate JWT token
        token = generate_token(
            user_id=user['id'],
            email=user['email'],
            role=user['role'],
            company_id=user['company_id']
        )
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'data': {
                'token': token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'role': user['role'],
                    'company_id': user['company_id']
                }
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT token
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'status': 'error',
                'message': 'Email and password are required'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        supabase = get_supabase_client()
        
        # Get user by email
        user_result = supabase.table('users').select('*').eq('email', email).execute()
        
        if not user_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401
        
        user = user_result.data[0]
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({
                'status': 'error',
                'message': 'Account is deactivated'
            }), 403
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401
        
        # Generate JWT token
        token = generate_token(
            user_id=user['id'],
            email=user['email'],
            role=user['role'],
            company_id=user['company_id']
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'token': token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'role': user['role'],
                    'company_id': user['company_id']
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Login failed: {str(e)}'
        }), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current user information from token
    Requires Authorization header with Bearer token
    """
    try:
        from utils.jwt_helper import get_token_from_header, decode_token
        
        # Get and decode token
        token = get_token_from_header()
        payload = decode_token(token)
        
        supabase = get_supabase_client()
        
        # Get user details
        user_result = supabase.table('users').select('*').eq('id', payload['user_id']).execute()
        
        if not user_result.data:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        user = user_result.data[0]
        
        return jsonify({
            'status': 'success',
            'data': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role'],
                'company_id': user['company_id'],
                'is_active': user['is_active']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user (client-side token removal)
    """
    return jsonify({
        'status': 'success',
        'message': 'Logout successful'
    }), 200
