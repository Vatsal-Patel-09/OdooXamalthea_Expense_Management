"""
User Management Routes (Admin Only)
Handles CRUD operations for users within a company
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from utils.auth import hash_password, token_required, admin_required
import re

users_bp = Blueprint('users', __name__)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_role(role: str) -> bool:
    """Validate user role"""
    return role in ['admin', 'manager', 'employee']

@users_bp.route('', methods=['GET'])
@token_required
def list_users(current_user):
    """
    List all users in the company
    
    Query Parameters:
    - role: Filter by role (admin, manager, employee)
    - is_active: Filter by active status (true/false)
    
    Response:
    {
        "success": true,
        "users": [ {...}, {...} ],
        "count": 10
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Build query
        query = supabase.table('users').select('*').eq('company_id', company_id)
        
        # Apply filters
        role_filter = request.args.get('role')
        if role_filter and validate_role(role_filter):
            query = query.eq('role', role_filter)
        
        is_active_filter = request.args.get('is_active')
        if is_active_filter:
            is_active = is_active_filter.lower() == 'true'
            query = query.eq('is_active', is_active)
        
        # Execute query
        response = query.order('created_at', desc=True).execute()
        users = response.data
        
        # Remove password_hash from all users
        for user in users:
            user.pop('password_hash', None)
        
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch users: {str(e)}'
        }), 500

@users_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """
    Get user details by ID
    
    Response:
    {
        "success": true,
        "user": { user_data }
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Fetch user
        response = supabase.table('users').select('*').eq('id', user_id).eq('company_id', company_id).execute()
        
        if not response.data:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user = response.data[0]
        user.pop('password_hash', None)
        
        # If user has a manager, fetch manager details
        if user.get('manager_id'):
            manager_response = supabase.table('users').select('id, name, email').eq('id', user['manager_id']).execute()
            if manager_response.data:
                user['manager'] = manager_response.data[0]
        
        return jsonify({
            'success': True,
            'user': user
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch user: {str(e)}'
        }), 500

@users_bp.route('', methods=['POST'])
@token_required
@admin_required
def create_user(current_user):
    """
    Create new user (employee or manager) - Admin only
    
    Request Body:
    {
        "email": "user@company.com",
        "password": "SecurePass123",
        "name": "John Doe",
        "role": "employee" | "manager",
        "manager_id": "uuid" (optional, required for employees)
    }
    
    Response:
    {
        "success": true,
        "message": "User created successfully",
        "user": { user_data }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'role']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        name = data['name'].strip()
        role = data['role'].lower()
        manager_id = data.get('manager_id')
        
        # Validate email
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        # Validate role
        if not validate_role(role):
            return jsonify({
                'success': False,
                'message': 'Invalid role. Must be admin, manager, or employee'
            }), 400
        
        # Admin cannot be created through this endpoint
        if role == 'admin':
            return jsonify({
                'success': False,
                'message': 'Cannot create admin users through this endpoint. Use signup instead.'
            }), 400
        
        # Validate password strength
        if len(password) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            }), 400
        
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Check if user already exists
        existing_user = supabase.table('users').select('id').eq('email', email).execute()
        if existing_user.data:
            return jsonify({
                'success': False,
                'message': 'User with this email already exists'
            }), 409
        
        # If manager_id provided, verify it exists and belongs to same company
        if manager_id:
            manager_response = supabase.table('users').select('id, company_id').eq('id', manager_id).execute()
            if not manager_response.data:
                return jsonify({
                    'success': False,
                    'message': 'Manager not found'
                }), 404
            
            if manager_response.data[0]['company_id'] != company_id:
                return jsonify({
                    'success': False,
                    'message': 'Manager must be from the same company'
                }), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'role': role,
            'company_id': company_id,
            'manager_id': manager_id,
            'is_active': True
        }
        
        user_response = supabase.table('users').insert(user_data).execute()
        
        if not user_response.data:
            return jsonify({
                'success': False,
                'message': 'Failed to create user'
            }), 500
        
        user = user_response.data[0]
        user.pop('password_hash', None)
        
        return jsonify({
            'success': True,
            'message': f'{role.capitalize()} created successfully',
            'user': user
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@users_bp.route('/<user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(current_user, user_id):
    """
    Update user information - Admin only
    
    Request Body:
    {
        "name": "Updated Name",
        "role": "manager",
        "manager_id": "uuid",
        "is_active": true
    }
    
    Response:
    {
        "success": true,
        "message": "User updated successfully",
        "user": { user_data }
    }
    """
    try:
        data = request.get_json()
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Check if user exists and belongs to same company
        user_response = supabase.table('users').select('*').eq('id', user_id).eq('company_id', company_id).execute()
        
        if not user_response.data:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        existing_user = user_response.data[0]
        
        # Prepare update data
        update_data = {}
        
        # Update name
        if 'name' in data:
            update_data['name'] = data['name'].strip()
        
        # Update role
        if 'role' in data:
            new_role = data['role'].lower()
            if not validate_role(new_role):
                return jsonify({
                    'success': False,
                    'message': 'Invalid role'
                }), 400
            
            # Cannot change admin role through this endpoint
            if existing_user['role'] == 'admin' or new_role == 'admin':
                return jsonify({
                    'success': False,
                    'message': 'Cannot modify admin role through this endpoint'
                }), 400
            
            update_data['role'] = new_role
        
        # Update manager
        if 'manager_id' in data:
            manager_id = data['manager_id']
            if manager_id:
                # Verify manager exists and belongs to same company
                manager_response = supabase.table('users').select('id, company_id').eq('id', manager_id).execute()
                if not manager_response.data:
                    return jsonify({
                        'success': False,
                        'message': 'Manager not found'
                    }), 404
                
                if manager_response.data[0]['company_id'] != company_id:
                    return jsonify({
                        'success': False,
                        'message': 'Manager must be from the same company'
                    }), 400
                
                # Cannot set self as manager
                if manager_id == user_id:
                    return jsonify({
                        'success': False,
                        'message': 'User cannot be their own manager'
                    }), 400
            
            update_data['manager_id'] = manager_id
        
        # Update active status
        if 'is_active' in data:
            update_data['is_active'] = bool(data['is_active'])
        
        if not update_data:
            return jsonify({
                'success': False,
                'message': 'No fields to update'
            }), 400
        
        # Update user
        update_response = supabase.table('users').update(update_data).eq('id', user_id).execute()
        
        if not update_response.data:
            return jsonify({
                'success': False,
                'message': 'Failed to update user'
            }), 500
        
        user = update_response.data[0]
        user.pop('password_hash', None)
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': user
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@users_bp.route('/<user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    """
    Deactivate user (soft delete) - Admin only
    
    Response:
    {
        "success": true,
        "message": "User deactivated successfully"
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Check if user exists and belongs to same company
        user_response = supabase.table('users').select('*').eq('id', user_id).eq('company_id', company_id).execute()
        
        if not user_response.data:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user = user_response.data[0]
        
        # Cannot delete admin users
        if user['role'] == 'admin':
            return jsonify({
                'success': False,
                'message': 'Cannot deactivate admin users'
            }), 400
        
        # Cannot delete self
        if user_id == current_user['user_id']:
            return jsonify({
                'success': False,
                'message': 'Cannot deactivate your own account'
            }), 400
        
        # Soft delete - set is_active to False
        update_response = supabase.table('users').update({'is_active': False}).eq('id', user_id).execute()
        
        if not update_response.data:
            return jsonify({
                'success': False,
                'message': 'Failed to deactivate user'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'User deactivated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@users_bp.route('/<user_id>/password', methods=['PUT'])
@token_required
@admin_required
def reset_password(current_user, user_id):
    """
    Reset user password - Admin only
    
    Request Body:
    {
        "new_password": "NewSecurePass123"
    }
    
    Response:
    {
        "success": true,
        "message": "Password reset successfully"
    }
    """
    try:
        data = request.get_json()
        
        if 'new_password' not in data:
            return jsonify({
                'success': False,
                'message': 'new_password is required'
            }), 400
        
        new_password = data['new_password']
        
        # Validate password strength
        if len(new_password) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            }), 400
        
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Check if user exists and belongs to same company
        user_response = supabase.table('users').select('id, role').eq('id', user_id).eq('company_id', company_id).execute()
        
        if not user_response.data:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Hash new password
        password_hash = hash_password(new_password)
        
        # Update password
        update_response = supabase.table('users').update({'password_hash': password_hash}).eq('id', user_id).execute()
        
        if not update_response.data:
            return jsonify({
                'success': False,
                'message': 'Failed to reset password'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
