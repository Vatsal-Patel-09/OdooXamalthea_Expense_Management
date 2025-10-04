"""
User Management Routes
Handles CRUD operations for users
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from middleware.auth import token_required, role_required
from utils.validators import validate_email, validate_password, validate_role
import bcrypt

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@token_required
def list_users(current_user):
    """
    List all users in the company
    Admins and managers can see all users
    Employees can only see themselves
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        user_role = current_user['role']
        
        # Build query based on role
        if user_role in ['admin', 'manager']:
            # Admins and managers can see all users in their company
            result = supabase.table('users').select('id, email, name, role, is_active, manager_id, created_at').eq('company_id', company_id).execute()
        else:
            # Employees can only see themselves
            result = supabase.table('users').select('id, email, name, role, is_active, manager_id, created_at').eq('id', current_user['user_id']).execute()
        
        return jsonify({
            'status': 'success',
            'data': result.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@users_bp.route('', methods=['POST'])
@token_required
@role_required('admin', 'manager')
def create_user(current_user):
    """
    Create a new user (Admin and Manager only)
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe",
            "role": "employee",
            "manager_id": "uuid" (optional)
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        name = data['name'].strip()
        role = data['role']
        manager_id = data.get('manager_id')
        
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
        
        # Validate role
        if not validate_role(role):
            return jsonify({
                'status': 'error',
                'message': 'Invalid role. Must be: admin, manager, or employee'
            }), 400
        
        # Only admins can create other admins
        if role == 'admin' and current_user['role'] != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Only admins can create admin users'
            }), 403
        
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
        
        # Create user
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'role': role,
            'company_id': current_user['company_id'],
            'manager_id': manager_id,
            'is_active': True
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create user'
            }), 500
        
        user = result.data[0]
        
        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'data': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role'],
                'is_active': user['is_active']
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@users_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """
    Get user details by ID
    """
    try:
        supabase = get_supabase_client()
        
        # Check permissions
        if current_user['role'] == 'employee' and current_user['user_id'] != user_id:
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        # Get user
        result = supabase.table('users').select('id, email, name, role, is_active, manager_id, company_id, created_at').eq('id', user_id).eq('company_id', current_user['company_id']).execute()
        
        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': result.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@users_bp.route('/<user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """
    Update user details
    Admins can update any user
    Managers can update employees
    Users can update themselves (limited fields)
    """
    try:
        data = request.get_json()
        supabase = get_supabase_client()
        
        # Get existing user
        existing_result = supabase.table('users').select('*').eq('id', user_id).eq('company_id', current_user['company_id']).execute()
        
        if not existing_result.data:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        existing_user = existing_result.data[0]
        
        # Check permissions
        is_self = current_user['user_id'] == user_id
        is_admin = current_user['role'] == 'admin'
        is_manager = current_user['role'] == 'manager'
        
        if not (is_self or is_admin or (is_manager and existing_user['role'] == 'employee')):
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        # Build update data
        update_data = {}
        
        # Fields that users can update themselves
        if 'name' in data:
            update_data['name'] = data['name'].strip()
        
        # Fields only admins/managers can update
        if is_admin or is_manager:
            if 'role' in data:
                if validate_role(data['role']):
                    # Only admins can change role to/from admin
                    if (data['role'] == 'admin' or existing_user['role'] == 'admin') and not is_admin:
                        return jsonify({
                            'status': 'error',
                            'message': 'Only admins can manage admin roles'
                        }), 403
                    update_data['role'] = data['role']
            
            if 'is_active' in data:
                update_data['is_active'] = bool(data['is_active'])
            
            if 'manager_id' in data:
                update_data['manager_id'] = data['manager_id']
        
        # Password update (anyone for themselves, admins for anyone)
        if 'password' in data:
            if is_self or is_admin:
                is_valid, error_msg = validate_password(data['password'])
                if not is_valid:
                    return jsonify({
                        'status': 'error',
                        'message': error_msg
                    }), 400
                password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                update_data['password_hash'] = password_hash
        
        if not update_data:
            return jsonify({
                'status': 'error',
                'message': 'No valid fields to update'
            }), 400
        
        # Update user
        result = supabase.table('users').update(update_data).eq('id', user_id).execute()
        
        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update user'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'User updated successfully',
            'data': {
                'id': result.data[0]['id'],
                'email': result.data[0]['email'],
                'name': result.data[0]['name'],
                'role': result.data[0]['role'],
                'is_active': result.data[0]['is_active']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@users_bp.route('/<user_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_user(current_user, user_id):
    """
    Delete user (Admin only)
    Cannot delete yourself
    """
    try:
        # Prevent self-deletion
        if current_user['user_id'] == user_id:
            return jsonify({
                'status': 'error',
                'message': 'Cannot delete your own account'
            }), 400
        
        supabase = get_supabase_client()
        
        # Check if user exists and is in same company
        existing_result = supabase.table('users').select('*').eq('id', user_id).eq('company_id', current_user['company_id']).execute()
        
        if not existing_result.data:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Delete user
        supabase.table('users').delete().eq('id', user_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'User deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
