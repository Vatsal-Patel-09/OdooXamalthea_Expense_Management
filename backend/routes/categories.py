"""
Category Management Routes
Handles CRUD operations for expense categories
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from middleware.auth import token_required, role_required

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('', methods=['GET'])
@token_required
def list_categories(current_user):
    """
    List all active categories in the company
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Get active categories
        result = supabase.table('categories').select('*').eq('company_id', company_id).eq('is_active', True).order('name').execute()
        
        return jsonify({
            'status': 'success',
            'data': result.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@categories_bp.route('', methods=['POST'])
@token_required
@role_required('admin', 'manager')
def create_category(current_user):
    """
    Create a new category (Admin and Manager only)
    
    Request Body:
        {
            "name": "Travel",
            "description": "Travel related expenses" (optional)
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'status': 'error',
                'message': 'Category name is required'
            }), 400
        
        name = data['name'].strip()
        description = data.get('description', '').strip()
        
        supabase = get_supabase_client()
        
        # Check if category already exists
        existing_category = supabase.table('categories').select('*').eq('name', name).eq('company_id', current_user['company_id']).execute()
        
        if existing_category.data:
            return jsonify({
                'status': 'error',
                'message': 'Category with this name already exists'
            }), 409
        
        # Create category
        category_data = {
            'name': name,
            'description': description,
            'company_id': current_user['company_id'],
            'is_active': True
        }
        
        result = supabase.table('categories').insert(category_data).execute()
        
        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create category'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Category created successfully',
            'data': result.data[0]
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@categories_bp.route('/<category_id>', methods=['GET'])
@token_required
def get_category(current_user, category_id):
    """
    Get category details by ID
    """
    try:
        supabase = get_supabase_client()
        
        # Get category
        result = supabase.table('categories').select('*').eq('id', category_id).eq('company_id', current_user['company_id']).execute()
        
        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'Category not found'
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

@categories_bp.route('/<category_id>', methods=['PUT'])
@token_required
@role_required('admin', 'manager')
def update_category(current_user, category_id):
    """
    Update category details (Admin and Manager only)
    
    Request Body:
        {
            "name": "Updated Name" (optional),
            "description": "Updated description" (optional),
            "is_active": true (optional)
        }
    """
    try:
        data = request.get_json()
        supabase = get_supabase_client()
        
        # Check if category exists
        existing_result = supabase.table('categories').select('*').eq('id', category_id).eq('company_id', current_user['company_id']).execute()
        
        if not existing_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Category not found'
            }), 404
        
        # Build update data
        update_data = {}
        
        if 'name' in data:
            name = data['name'].strip()
            # Check if new name conflicts with existing category
            name_check = supabase.table('categories').select('*').eq('name', name).eq('company_id', current_user['company_id']).neq('id', category_id).execute()
            if name_check.data:
                return jsonify({
                    'status': 'error',
                    'message': 'Category with this name already exists'
                }), 409
            update_data['name'] = name
        
        if 'description' in data:
            update_data['description'] = data['description'].strip()
        
        if 'is_active' in data:
            update_data['is_active'] = bool(data['is_active'])
        
        if not update_data:
            return jsonify({
                'status': 'error',
                'message': 'No valid fields to update'
            }), 400
        
        # Update category
        result = supabase.table('categories').update(update_data).eq('id', category_id).execute()
        
        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update category'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Category updated successfully',
            'data': result.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@categories_bp.route('/<category_id>', methods=['DELETE'])
@token_required
@role_required('admin', 'manager')
def delete_category(current_user, category_id):
    """
    Delete/deactivate category (Admin and Manager only)
    Soft delete by setting is_active to False
    """
    try:
        supabase = get_supabase_client()
        
        # Check if category exists
        existing_result = supabase.table('categories').select('*').eq('id', category_id).eq('company_id', current_user['company_id']).execute()
        
        if not existing_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Category not found'
            }), 404
        
        # Soft delete - set is_active to False
        result = supabase.table('categories').update({'is_active': False}).eq('id', category_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Category deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
