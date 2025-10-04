"""
Authentication Routes
Handles user signup, login, and authentication
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from utils.auth import hash_password, verify_password, generate_token, token_required
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, ""

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Admin signup endpoint - Creates admin user and company
    
    Request Body:
    {
        "email": "admin@company.com",
        "password": "SecurePass123",
        "name": "Admin Name",
        "company_name": "Company Inc.",
        "currency": "USD" (optional, default: USD)
    }
    
    Response:
    {
        "success": true,
        "message": "Admin account created successfully",
        "token": "jwt_token_here",
        "user": { user_data },
        "company": { company_data }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'company_name']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        name = data['name'].strip()
        company_name = data['company_name'].strip()
        currency = data.get('currency', 'USD').upper()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        # Validate password strength
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_msg
            }), 400
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Check if user already exists
        existing_user = supabase.table('users').select('id').eq('email', email).execute()
        if existing_user.data:
            return jsonify({
                'success': False,
                'message': 'User with this email already exists'
            }), 409
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create company first
        company_data = {
            'name': company_name,
            'currency': currency
        }
        company_response = supabase.table('companies').insert(company_data).execute()
        
        if not company_response.data:
            return jsonify({
                'success': False,
                'message': 'Failed to create company'
            }), 500
        
        company = company_response.data[0]
        company_id = company['id']
        
        # Update company with created_by (will be set after user creation)
        # Create admin user
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'role': 'admin',
            'company_id': company_id,
            'is_active': True
        }
        user_response = supabase.table('users').insert(user_data).execute()
        
        if not user_response.data:
            # Rollback: Delete company if user creation fails
            supabase.table('companies').delete().eq('id', company_id).execute()
            return jsonify({
                'success': False,
                'message': 'Failed to create user account'
            }), 500
        
        user = user_response.data[0]
        user_id = user['id']
        
        # Update company's created_by field
        supabase.table('companies').update({'created_by': user_id}).eq('id', company_id).execute()
        
        # Generate JWT token
        token = generate_token(
            user_id=user_id,
            email=user['email'],
            role=user['role'],
            company_id=company_id
        )
        
        # Remove password_hash from response
        user.pop('password_hash', None)
        
        return jsonify({
            'success': True,
            'message': 'Admin account created successfully',
            'token': token,
            'user': user,
            'company': company
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    Request Body:
    {
        "email": "user@company.com",
        "password": "SecurePass123"
    }
    
    Response:
    {
        "success": true,
        "message": "Login successful",
        "token": "jwt_token_here",
        "user": { user_data }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Find user by email
        user_response = supabase.table('users').select('*').eq('email', email).execute()
        
        if not user_response.data:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        user = user_response.data[0]
        
        # Check if user is active
        if not user.get('is_active', False):
            return jsonify({
                'success': False,
                'message': 'Account is deactivated. Contact your administrator.'
            }), 403
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        # Generate JWT token
        token = generate_token(
            user_id=user['id'],
            email=user['email'],
            role=user['role'],
            company_id=user['company_id']
        )
        
        # Remove password_hash from response
        user.pop('password_hash', None)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': user
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """
    Get current authenticated user's information
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
    {
        "success": true,
        "user": { user_data }
    }
    """
    try:
        supabase = get_supabase_client()
        
        # Fetch user details from database
        user_response = supabase.table('users').select('*').eq('id', current_user['user_id']).execute()
        
        if not user_response.data:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user = user_response.data[0]
        user.pop('password_hash', None)
        
        return jsonify({
            'success': True,
            'user': user
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
