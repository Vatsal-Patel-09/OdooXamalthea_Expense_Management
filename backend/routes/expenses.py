"""
Expense Routes
Handles expense CRUD operations and submission for approval
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from utils.auth import token_required, admin_required
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import re

expenses_bp = Blueprint('expenses', __name__)


def validate_expense_data(data, is_update=False):
    """Validate expense data"""
    errors = []
    
    if not is_update or 'category_id' in data:
        if not data.get('category_id'):
            errors.append('category_id is required')
    
    if not is_update or 'amount' in data:
        amount = data.get('amount')
        if not amount or float(amount) <= 0:
            errors.append('amount must be greater than 0')
    
    if not is_update or 'currency' in data:
        if not data.get('currency'):
            errors.append('currency is required')
    
    if not is_update or 'expense_date' in data:
        if not data.get('expense_date'):
            errors.append('expense_date is required')
    
    if not is_update or 'paid_by' in data:
        paid_by = data.get('paid_by')
        if paid_by not in ['personal', 'company']:
            errors.append('paid_by must be either "personal" or "company"')
    
    return errors


@expenses_bp.route('', methods=['GET'])
@token_required
def list_expenses(current_user):
    """
    Get list of expenses with filters
    
    GET /api/expenses?status=draft&category_id=123&user_id=456&from_date=2024-01-01&to_date=2024-12-31
    
    Query Parameters:
    - status: Filter by status (draft, submitted, approved, rejected)
    - category_id: Filter by category
    - user_id: Filter by user (admin/manager only)
    - from_date: Filter by expense_date >= from_date
    - to_date: Filter by expense_date <= to_date
    - paid_by: Filter by paid_by (personal, company)
    
    Response:
    {
        "success": true,
        "message": "Expenses retrieved successfully",
        "data": [...]
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        user_id = current_user['user_id']
        role = current_user['role']
        
        # Base query - filter by company
        query = supabase.table('expenses').select('*, category:categories(name), user:users(name, email)').eq('company_id', company_id)
        
        # Non-admins can only see their own expenses
        if role not in ['admin', 'manager']:
            query = query.eq('user_id', user_id)
        
        # Apply filters
        status = request.args.get('status')
        if status:
            query = query.eq('status', status)
        
        category_id = request.args.get('category_id')
        if category_id:
            query = query.eq('category_id', category_id)
        
        # User filter (only for admin/manager)
        filter_user_id = request.args.get('user_id')
        if filter_user_id and role in ['admin', 'manager']:
            query = query.eq('user_id', filter_user_id)
        
        # Date range filters
        from_date = request.args.get('from_date')
        if from_date:
            query = query.gte('expense_date', from_date)
        
        to_date = request.args.get('to_date')
        if to_date:
            query = query.lte('expense_date', to_date)
        
        # Paid by filter
        paid_by = request.args.get('paid_by')
        if paid_by:
            query = query.eq('paid_by', paid_by)
        
        # Order by expense date (most recent first)
        query = query.order('expense_date', desc=True)
        
        # Execute query
        result = query.execute()
        
        return jsonify({
            'success': True,
            'message': 'Expenses retrieved successfully',
            'data': result.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve expenses: {str(e)}'
        }), 500


@expenses_bp.route('/<expense_id>', methods=['GET'])
@token_required
def get_expense(current_user, expense_id):
    """
    Get single expense by ID
    
    GET /api/expenses/:id
    
    Response:
    {
        "success": true,
        "message": "Expense retrieved successfully",
        "data": {...}
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        user_id = current_user['user_id']
        role = current_user['role']
        
        # Get expense with related data
        result = supabase.table('expenses').select(
            '*, category:categories(name), user:users(name, email)'
        ).eq('id', expense_id).eq('company_id', company_id).execute()
        
        if not result.data:
            return jsonify({
                'success': False,
                'message': 'Expense not found'
            }), 404
        
        expense = result.data[0]
        
        # Check if user has permission to view
        if role not in ['admin', 'manager'] and expense['user_id'] != user_id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized: You can only view your own expenses'
            }), 403
        
        return jsonify({
            'success': True,
            'message': 'Expense retrieved successfully',
            'data': expense
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve expense: {str(e)}'
        }), 500


@expenses_bp.route('', methods=['POST'])
@token_required
def create_expense(current_user):
    """
    Create new expense (draft status)
    
    POST /api/expenses
    Request Body:
    {
        "category_id": 123,
        "amount": 100.50,
        "currency": "USD",
        "expense_date": "2024-01-15",
        "description": "Office supplies",
        "receipt_url": "https://...",
        "paid_by": "personal"
    }
    
    Response:
    {
        "success": true,
        "message": "Expense created successfully",
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
        errors = validate_expense_data(data)
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        user_id = current_user['user_id']
        
        # Verify category exists and belongs to company
        category_result = supabase.table('categories').select('id, is_active').eq(
            'id', data['category_id']
        ).eq('company_id', company_id).execute()
        
        if not category_result.data:
            return jsonify({
                'success': False,
                'message': 'Category not found or does not belong to your company'
            }), 404
        
        if not category_result.data[0]['is_active']:
            return jsonify({
                'success': False,
                'message': 'Cannot create expense with inactive category'
            }), 400
        
        # Create expense
        expense_data = {
            'company_id': company_id,
            'user_id': user_id,
            'category_id': data['category_id'],
            'amount': str(Decimal(str(data['amount'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'currency': data['currency'],
            'expense_date': data['expense_date'],
            'description': data.get('description', ''),
            'receipt_url': data.get('receipt_url'),
            'paid_by': data['paid_by'],
            'status': 'draft'
        }
        
        result = supabase.table('expenses').insert(expense_data).execute()
        
        return jsonify({
            'success': True,
            'message': 'Expense created successfully',
            'data': result.data[0]
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to create expense: {str(e)}'
        }), 500


@expenses_bp.route('/<expense_id>', methods=['PUT'])
@token_required
def update_expense(current_user, expense_id):
    """
    Update expense (only draft expenses can be edited)
    
    PUT /api/expenses/:id
    Request Body:
    {
        "category_id": 123,
        "amount": 150.00,
        "description": "Updated description",
        ...
    }
    
    Response:
    {
        "success": true,
        "message": "Expense updated successfully",
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
        user_id = current_user['user_id']
        role = current_user['role']
        
        # Get existing expense
        existing = supabase.table('expenses').select('*').eq(
            'id', expense_id
        ).eq('company_id', company_id).execute()
        
        if not existing.data:
            return jsonify({
                'success': False,
                'message': 'Expense not found'
            }), 404
        
        expense = existing.data[0]
        
        # Check ownership
        if role not in ['admin'] and expense['user_id'] != user_id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized: You can only update your own expenses'
            }), 403
        
        # Only draft expenses can be edited
        if expense['status'] != 'draft':
            return jsonify({
                'success': False,
                'message': f'Cannot update expense with status: {expense["status"]}. Only draft expenses can be edited.'
            }), 400
        
        # Validate data
        errors = validate_expense_data(data, is_update=True)
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        # If category is being changed, verify it
        if 'category_id' in data:
            category_result = supabase.table('categories').select('id, is_active').eq(
                'id', data['category_id']
            ).eq('company_id', company_id).execute()
            
            if not category_result.data:
                return jsonify({
                    'success': False,
                    'message': 'Category not found or does not belong to your company'
                }), 404
            
            if not category_result.data[0]['is_active']:
                return jsonify({
                    'success': False,
                    'message': 'Cannot update expense with inactive category'
                }), 400
        
        # Build update data
        update_data = {}
        allowed_fields = ['category_id', 'amount', 'currency', 'expense_date', 'description', 'receipt_url', 'paid_by']
        
        for field in allowed_fields:
            if field in data:
                if field == 'amount':
                    update_data[field] = str(Decimal(str(data[field])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                else:
                    update_data[field] = data[field]
        
        # Update expense
        result = supabase.table('expenses').update(update_data).eq('id', expense_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Expense updated successfully',
            'data': result.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to update expense: {str(e)}'
        }), 500


@expenses_bp.route('/<expense_id>', methods=['DELETE'])
@token_required
def delete_expense(current_user, expense_id):
    """
    Delete expense (only draft expenses can be deleted)
    
    DELETE /api/expenses/:id
    
    Response:
    {
        "success": true,
        "message": "Expense deleted successfully"
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        user_id = current_user['user_id']
        role = current_user['role']
        
        # Get existing expense
        existing = supabase.table('expenses').select('*').eq(
            'id', expense_id
        ).eq('company_id', company_id).execute()
        
        if not existing.data:
            return jsonify({
                'success': False,
                'message': 'Expense not found'
            }), 404
        
        expense = existing.data[0]
        
        # Check ownership
        if role not in ['admin'] and expense['user_id'] != user_id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized: You can only delete your own expenses'
            }), 403
        
        # Only draft expenses can be deleted
        if expense['status'] != 'draft':
            return jsonify({
                'success': False,
                'message': f'Cannot delete expense with status: {expense["status"]}. Only draft expenses can be deleted.'
            }), 400
        
        # Delete expense
        supabase.table('expenses').delete().eq('id', expense_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Expense deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to delete expense: {str(e)}'
        }), 500


@expenses_bp.route('/<expense_id>/submit', methods=['POST'])
@token_required
def submit_expense(current_user, expense_id):
    """
    Submit expense for approval
    
    POST /api/expenses/:id/submit
    
    Response:
    {
        "success": true,
        "message": "Expense submitted for approval",
        "data": {...}
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        user_id = current_user['user_id']
        
        # Get existing expense
        existing = supabase.table('expenses').select('*').eq(
            'id', expense_id
        ).eq('company_id', company_id).eq('user_id', user_id).execute()
        
        if not existing.data:
            return jsonify({
                'success': False,
                'message': 'Expense not found or does not belong to you'
            }), 404
        
        expense = existing.data[0]
        
        # Can only submit draft expenses
        if expense['status'] != 'draft':
            return jsonify({
                'success': False,
                'message': f'Cannot submit expense with status: {expense["status"]}. Only draft expenses can be submitted.'
            }), 400
        
        # Update status to submitted
        result = supabase.table('expenses').update({
            'status': 'submitted',
            'submitted_at': datetime.now().isoformat()
        }).eq('id', expense_id).execute()
        
        # TODO: In Phase 4, trigger approval workflow here
        # - Find matching approval rule
        # - Create approval records
        # - Send notifications to approvers
        
        return jsonify({
            'success': True,
            'message': 'Expense submitted for approval',
            'data': result.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to submit expense: {str(e)}'
        }), 500


@expenses_bp.route('/stats', methods=['GET'])
@token_required
def get_expense_stats(current_user):
    """
    Get expense statistics for current user
    
    GET /api/expenses/stats
    
    Response:
    {
        "success": true,
        "message": "Statistics retrieved successfully",
        "data": {
            "total_expenses": 10,
            "draft_count": 2,
            "submitted_count": 3,
            "approved_count": 4,
            "rejected_count": 1,
            "total_amount": 5000.00,
            "approved_amount": 3000.00
        }
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        user_id = current_user['user_id']
        role = current_user['role']
        
        # Base query
        if role in ['admin', 'manager']:
            # Admins/managers see company-wide stats
            result = supabase.table('expenses').select('status, amount, currency').eq('company_id', company_id).execute()
        else:
            # Regular users see only their stats
            result = supabase.table('expenses').select('status, amount, currency').eq(
                'company_id', company_id
            ).eq('user_id', user_id).execute()
        
        expenses = result.data
        
        # Calculate statistics
        stats = {
            'total_expenses': len(expenses),
            'draft_count': len([e for e in expenses if e['status'] == 'draft']),
            'submitted_count': len([e for e in expenses if e['status'] == 'submitted']),
            'approved_count': len([e for e in expenses if e['status'] == 'approved']),
            'rejected_count': len([e for e in expenses if e['status'] == 'rejected']),
            'total_amount': sum(float(e['amount']) for e in expenses),
            'approved_amount': sum(float(e['amount']) for e in expenses if e['status'] == 'approved')
        }
        
        return jsonify({
            'success': True,
            'message': 'Statistics retrieved successfully',
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve statistics: {str(e)}'
        }), 500
