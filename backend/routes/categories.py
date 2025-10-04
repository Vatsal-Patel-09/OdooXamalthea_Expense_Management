"""
Category Routes
Handles expense category management (Admin only for create/update/delete)
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from utils.auth import token_required, admin_required
import re

categories_bp = Blueprint('categories', __name__)


def validate_category_name(name: str) -> bool:
    """Validate category name (alphanumeric, spaces, hyphens, max 100 chars)"""
    if not name or len(name.strip()) == 0:
        return False
    if len(name) > 100:
        return False
    # Allow letters, numbers, spaces, hyphens, underscores
    pattern = r'^[a-zA-Z0-9\s\-_]+$'
    return bool(re.match(pattern, name.strip()))


@categories_bp.route('', methods=['GET'])
@token_required
def list_categories(current_user):
    """
    Get all categories for the company
    
    GET /api/categories?is_active=true
    
    Query Parameters:
    - is_active (optional): Filter by active status (true/false)
    
    Response:
    {
        "success": true,
        "data": [
            {
                "id": "uuid",
                "name": "Travel",
                "description": "Travel expenses",
                "is_active": true,
                "created_at": "2025-10-04T..."
            },
            ...
        ],
        "count": 10
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Build query
        query = supabase.table('categories').select('*').eq('company_id', company_id)
        
        # Filter by active status if provided
        is_active = request.args.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            query = query.eq('is_active', is_active_bool)
        
        # Order by name
        query = query.order('name')
        
        response = query.execute()
        
        return jsonify({
            'success': True,
            'data': response.data,
            'count': len(response.data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch categories: {str(e)}'
        }), 500


@categories_bp.route('/<category_id>', methods=['GET'])
@token_required
def get_category(current_user, category_id):
    """
    Get single category by ID
    
    GET /api/categories/:id
    
    Response:
    {
        "success": true,
        "data": {
            "id": "uuid",
            "name": "Travel",
            "description": "Travel expenses",
            "is_active": true,
            ...
        }
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        response = supabase.table('categories').select('*').eq('id', category_id).eq('company_id', company_id).execute()
        
        if not response.data:
            return jsonify({
                'success': False,
                'message': 'Category not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': response.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch category: {str(e)}'
        }), 500


@categories_bp.route('', methods=['POST'])
@token_required
@admin_required
def create_category(current_user):
    """
    Create new category (Admin only)
    
    POST /api/categories
    Request Body:
    {
        "name": "Travel",
        "description": "Business travel expenses" (optional)
    }
    
    Response:
    {
        "success": true,
        "message": "Category created successfully",
        "data": { category_data }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'name' not in data:
            return jsonify({
                'success': False,
                'message': 'Category name is required'
            }), 400
        
        name = data['name'].strip()
        description = data.get('description', '').strip()
        
        # Validate name
        if not validate_category_name(name):
            return jsonify({
                'success': False,
                'message': 'Invalid category name. Use only letters, numbers, spaces, hyphens, and underscores (max 100 chars)'
            }), 400
        
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Check if category already exists for this company
        existing = supabase.table('categories').select('id').eq('name', name).eq('company_id', company_id).execute()
        
        if existing.data:
            return jsonify({
                'success': False,
                'message': f'Category "{name}" already exists in your company'
            }), 409
        
        # Create category
        new_category = {
            'name': name,
            'description': description,
            'company_id': company_id,
            'is_active': True
        }
        
        response = supabase.table('categories').insert(new_category).execute()
        
        return jsonify({
            'success': True,
            'message': 'Category created successfully',
            'data': response.data[0]
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to create category: {str(e)}'
        }), 500


@categories_bp.route('/<category_id>', methods=['PUT'])
@token_required
@admin_required
def update_category(current_user, category_id):
    """
    Update category (Admin only)
    
    PUT /api/categories/:id
    Request Body:
    {
        "name": "Updated Name" (optional),
        "description": "Updated description" (optional),
        "is_active": true/false (optional)
    }
    
    Response:
    {
        "success": true,
        "message": "Category updated successfully",
        "data": { updated_category }
    }
    """
    try:
        data = request.get_json()
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Check if category exists
        existing = supabase.table('categories').select('*').eq('id', category_id).eq('company_id', company_id).execute()
        
        if not existing.data:
            return jsonify({
                'success': False,
                'message': 'Category not found'
            }), 404
        
        # Build update object
        updates = {}
        
        if 'name' in data:
            name = data['name'].strip()
            if not validate_category_name(name):
                return jsonify({
                    'success': False,
                    'message': 'Invalid category name'
                }), 400
            
            # Check if new name conflicts with existing category
            if name != existing.data[0]['name']:
                name_check = supabase.table('categories').select('id').eq('name', name).eq('company_id', company_id).execute()
                if name_check.data:
                    return jsonify({
                        'success': False,
                        'message': f'Category "{name}" already exists'
                    }), 409
            
            updates['name'] = name
        
        if 'description' in data:
            updates['description'] = data['description'].strip()
        
        if 'is_active' in data:
            updates['is_active'] = bool(data['is_active'])
        
        if not updates:
            return jsonify({
                'success': False,
                'message': 'No fields to update'
            }), 400
        
        # Update category
        response = supabase.table('categories').update(updates).eq('id', category_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Category updated successfully',
            'data': response.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to update category: {str(e)}'
        }), 500


@categories_bp.route('/<category_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_category(current_user, category_id):
    """
    Deactivate category (Admin only)
    Soft delete - sets is_active to false
    
    DELETE /api/categories/:id
    
    Response:
    {
        "success": true,
        "message": "Category deactivated successfully"
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Check if category exists
        existing = supabase.table('categories').select('*').eq('id', category_id).eq('company_id', company_id).execute()
        
        if not existing.data:
            return jsonify({
                'success': False,
                'message': 'Category not found'
            }), 404
        
        # Check if category is used by any expenses
        expenses = supabase.table('expenses').select('id').eq('category_id', category_id).limit(1).execute()
        
        if expenses.data:
            # Soft delete - just deactivate
            supabase.table('categories').update({'is_active': False}).eq('id', category_id).execute()
            
            return jsonify({
                'success': True,
                'message': 'Category deactivated successfully (has existing expenses)'
            }), 200
        else:
            # No expenses, can actually delete
            supabase.table('categories').delete().eq('id', category_id).execute()
            
            return jsonify({
                'success': True,
                'message': 'Category deleted successfully'
            }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to delete category: {str(e)}'
        }), 500
