"""
Approval Rules Routes
Handles approval rule configuration and management
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from utils.auth import token_required, admin_required
from datetime import datetime

approval_rules_bp = Blueprint('approval_rules', __name__)


def validate_rule_data(data, is_update=False):
    """Validate approval rule data"""
    errors = []
    
    if not is_update or 'name' in data:
        if not data.get('name'):
            errors.append('name is required')
    
    if not is_update or 'currency_code' in data:
        if not data.get('currency_code'):
            errors.append('currency_code is required')
    
    if not is_update or 'min_amount' in data:
        min_amount = data.get('min_amount', 0)
        if float(min_amount) < 0:
            errors.append('min_amount cannot be negative')
    
    if not is_update or 'max_amount' in data:
        max_amount = data.get('max_amount')
        if max_amount is not None and float(max_amount) < 0:
            errors.append('max_amount cannot be negative')
    
    # Validate min_amount < max_amount
    if 'min_amount' in data and 'max_amount' in data:
        min_amt = float(data.get('min_amount', 0))
        max_amt = data.get('max_amount')
        if max_amt is not None and min_amt >= float(max_amt):
            errors.append('min_amount must be less than max_amount')
    
    if not is_update or 'approval_percentage' in data:
        percentage = data.get('approval_percentage', 100)
        try:
            percentage_int = int(percentage)
            if not (0 < percentage_int <= 100):
                errors.append('approval_percentage must be between 1 and 100')
        except (ValueError, TypeError):
            errors.append('approval_percentage must be an integer')
    
    if not is_update or 'priority' in data:
        priority = data.get('priority', 1)
        if priority is not None:
            try:
                priority_int = int(priority)
                if priority_int < 1 or priority_int > 10:
                    errors.append('priority must be between 1 and 10')
            except (ValueError, TypeError):
                errors.append('priority must be an integer')
    
    return errors


@approval_rules_bp.route('', methods=['GET'])
@token_required
def list_approval_rules(current_user):
    """
    Get list of approval rules for the company
    
    GET /api/approval-rules?is_active=true&category_id=123
    
    Query Parameters:
    - is_active: Filter by active status (true/false)
    - category_id: Filter by category
    
    Response:
    {
        "success": true,
        "message": "Approval rules retrieved successfully",
        "data": [...]
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Base query - get rules with category and approvers
        query = supabase.table('approval_rules').select(
            '*, category:categories(id, name), approvers:approval_rule_approvers(approver_user_id, order_index, users(id, name, email, role))'
        ).eq('company_id', company_id)
        
        # Apply filters
        is_active = request.args.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            query = query.eq('is_active', is_active_bool)
        
        category_id = request.args.get('category_id')
        if category_id:
            query = query.eq('category_id', category_id)
        
        # Order by name
        query = query.order('name')
        
        result = query.execute()
        
        return jsonify({
            'success': True,
            'message': 'Approval rules retrieved successfully',
            'data': result.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve approval rules: {str(e)}'
        }), 500


@approval_rules_bp.route('/<rule_id>', methods=['GET'])
@token_required
def get_approval_rule(current_user, rule_id):
    """
    Get single approval rule by ID
    
    GET /api/approval-rules/:id
    
    Response:
    {
        "success": true,
        "message": "Approval rule retrieved successfully",
        "data": {...}
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        result = supabase.table('approval_rules').select(
            '*, category:categories(id, name), approvers:approval_rule_approvers(approver_user_id, order_index, users(id, name, email, role))'
        ).eq('id', rule_id).eq('company_id', company_id).execute()
        
        if not result.data:
            return jsonify({
                'success': False,
                'message': 'Approval rule not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Approval rule retrieved successfully',
            'data': result.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve approval rule: {str(e)}'
        }), 500


@approval_rules_bp.route('', methods=['POST'])
@token_required
@admin_required
def create_approval_rule(current_user):
    """
    Create new approval rule (admin only)
    
    POST /api/approval-rules
    Request Body:
    {
        "name": "Travel Expenses",
        "description": "Approval for travel expenses",
        "category_id": "uuid-123",
        "min_amount": 0,
        "max_amount": 1000,
        "is_sequential": false,
        "approval_percentage": 100,
        "approver_user_ids": ["user-1", "user-2"]
    }
    
    Response:
    {
        "success": true,
        "message": "Approval rule created successfully",
        "data": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        # Validate data
        errors = validate_rule_data(data)
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # If category_id provided, verify it exists
        if data.get('category_id'):
            category_result = supabase.table('categories').select('id').eq(
                'id', data['category_id']
            ).eq('company_id', company_id).execute()
            
            if not category_result.data:
                return jsonify({
                    'success': False,
                    'message': 'Category not found or does not belong to your company'
                }), 404
        
        # Create approval rule
        rule_data = {
            'company_id': company_id,
            'name': data['name'],
            'description': data.get('description', ''),
            'category_id': data.get('category_id'),
            'currency_code': data.get('currency_code', 'USD'),  # Added currency_code
            'min_amount': float(data.get('min_amount', 0)),
            'max_amount': float(data['max_amount']) if data.get('max_amount') else None,
            'priority': int(data.get('priority', 1)),  # Added priority as integer
            'is_sequential': data.get('is_sequential', False),
            'approval_percentage': int(data.get('approval_percentage', 100)),  # Changed to int
            'is_active': True
        }
        
        result = supabase.table('approval_rules').insert(rule_data).execute()
        rule = result.data[0]
        
        # Add approvers if provided
        approver_user_ids = data.get('approver_user_ids', [])
        if approver_user_ids:
            approvers = []
            for index, user_id in enumerate(approver_user_ids):
                # Verify user exists and is manager/admin
                user_result = supabase.table('users').select('id, role').eq(
                    'id', user_id
                ).eq('company_id', company_id).execute()
                
                if not user_result.data:
                    continue  # Skip invalid users
                
                user = user_result.data[0]
                if user['role'] not in ['manager', 'admin']:
                    continue  # Skip non-approvers
                
                approvers.append({
                    'rule_id': rule['id'],
                    'approver_user_id': user_id,
                    'order_index': index
                })
            
            if approvers:
                supabase.table('approval_rule_approvers').insert(approvers).execute()
        
        # Fetch complete rule with approvers
        complete_rule = supabase.table('approval_rules').select(
            '*, category:categories(id, name), approvers:approval_rule_approvers(approver_user_id, order_index, users(id, name, email, role))'
        ).eq('id', rule['id']).execute()
        
        return jsonify({
            'success': True,
            'message': 'Approval rule created successfully',
            'data': complete_rule.data[0]
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to create approval rule: {str(e)}'
        }), 500


@approval_rules_bp.route('/<rule_id>', methods=['PUT'])
@token_required
@admin_required
def update_approval_rule(current_user, rule_id):
    """
    Update approval rule (admin only)
    
    PUT /api/approval-rules/:id
    Request Body:
    {
        "name": "Updated name",
        "max_amount": 2000,
        "is_active": false,
        "approver_user_ids": ["user-1", "user-3"]
    }
    
    Response:
    {
        "success": true,
        "message": "Approval rule updated successfully",
        "data": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Verify rule exists
        existing = supabase.table('approval_rules').select('*').eq(
            'id', rule_id
        ).eq('company_id', company_id).execute()
        
        if not existing.data:
            return jsonify({
                'success': False,
                'message': 'Approval rule not found'
            }), 404
        
        # Validate data
        errors = validate_rule_data(data, is_update=True)
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        # Build update data
        update_data = {}
        allowed_fields = ['name', 'description', 'category_id', 'currency_code', 'min_amount', 
                         'max_amount', 'priority', 'is_sequential', 'approval_percentage', 'is_active']
        
        for field in allowed_fields:
            if field in data:
                if field == 'min_amount':
                    update_data[field] = float(data[field])
                elif field == 'approval_percentage':
                    update_data[field] = int(data[field])  # Changed to int
                elif field == 'max_amount':
                    update_data[field] = float(data[field]) if data[field] else None
                elif field == 'priority':
                    update_data[field] = int(data[field]) if data[field] else 1
                else:
                    update_data[field] = data[field]
        
        # Update rule
        result = supabase.table('approval_rules').update(update_data).eq('id', rule_id).execute()
        
        # Update approvers if provided
        if 'approver_user_ids' in data:
            # Delete existing approvers
            supabase.table('approval_rule_approvers').delete().eq('rule_id', rule_id).execute()
            
            # Add new approvers
            approver_user_ids = data['approver_user_ids']
            if approver_user_ids:
                approvers = []
                for index, user_id in enumerate(approver_user_ids):
                    user_result = supabase.table('users').select('id, role').eq(
                        'id', user_id
                    ).eq('company_id', company_id).execute()
                    
                    if not user_result.data:
                        continue
                    
                    user = user_result.data[0]
                    if user['role'] not in ['manager', 'admin']:
                        continue
                    
                    approvers.append({
                        'rule_id': rule_id,
                        'approver_user_id': user_id,
                        'order_index': index
                    })
                
                if approvers:
                    supabase.table('approval_rule_approvers').insert(approvers).execute()
        
        # Fetch complete updated rule
        complete_rule = supabase.table('approval_rules').select(
            '*, category:categories(id, name), approvers:approval_rule_approvers(approver_user_id, order_index, users(id, name, email, role))'
        ).eq('id', rule_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Approval rule updated successfully',
            'data': complete_rule.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to update approval rule: {str(e)}'
        }), 500


@approval_rules_bp.route('/<rule_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_approval_rule(current_user, rule_id):
    """
    Delete approval rule (admin only)
    
    DELETE /api/approval-rules/:id
    
    Response:
    {
        "success": true,
        "message": "Approval rule deleted successfully"
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Verify rule exists
        existing = supabase.table('approval_rules').select('*').eq(
            'id', rule_id
        ).eq('company_id', company_id).execute()
        
        if not existing.data:
            return jsonify({
                'success': False,
                'message': 'Approval rule not found'
            }), 404
        
        # Check if rule is being used by any approvals
        approvals_check = supabase.table('approvals').select('id').eq('rule_id', rule_id).limit(1).execute()
        
        if approvals_check.data:
            # Soft delete - just mark as inactive
            supabase.table('approval_rules').update({'is_active': False}).eq('id', rule_id).execute()
            return jsonify({
                'success': True,
                'message': 'Approval rule deactivated (has associated approvals)'
            }), 200
        
        # Hard delete - no approvals associated
        # First delete approvers
        supabase.table('approval_rule_approvers').delete().eq('rule_id', rule_id).execute()
        
        # Then delete rule
        supabase.table('approval_rules').delete().eq('id', rule_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Approval rule deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to delete approval rule: {str(e)}'
        }), 500
