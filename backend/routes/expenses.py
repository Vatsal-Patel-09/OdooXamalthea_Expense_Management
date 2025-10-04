"""
Expense Management Routes
Handles CRUD operations for expenses
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from middleware.auth import token_required, role_required
from utils.validators import validate_expense_status
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('', methods=['GET'])
@token_required
def list_expenses(current_user):
    """
    List expenses based on user role
    - Employees: See only their own expenses
    - Managers: See their team's expenses (employees under them)
    - Admins: See all company expenses
    
    Query Parameters:
        status: Filter by status (draft, submitted, approved, rejected)
        category_id: Filter by category
        start_date: Filter by start date (YYYY-MM-DD)
        end_date: Filter by end date (YYYY-MM-DD)
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        user_role = current_user['role']
        user_id = current_user['user_id']
        
        # Start building query
        query = supabase.table('expenses').select('*, users!expenses_user_id_fkey(name, email), categories(name)').eq('company_id', company_id)
        
        # Role-based filtering
        if user_role == 'employee':
            # Employees see only their expenses
            query = query.eq('user_id', user_id)
        elif user_role == 'manager':
            # Managers see their team's expenses
            # First get employees under this manager
            team_result = supabase.table('users').select('id').eq('manager_id', user_id).execute()
            team_ids = [user_id] + [emp['id'] for emp in team_result.data]
            query = query.in_('user_id', team_ids)
        # Admins see all (no additional filter)
        
        # Apply query parameter filters
        status = request.args.get('status')
        if status:
            if validate_expense_status(status):
                query = query.eq('status', status)
        
        category_id = request.args.get('category_id')
        if category_id:
            query = query.eq('category_id', category_id)
        
        start_date = request.args.get('start_date')
        if start_date:
            query = query.gte('expense_date', start_date)
        
        end_date = request.args.get('end_date')
        if end_date:
            query = query.lte('expense_date', end_date)
        
        # Execute query
        result = query.order('expense_date', desc=True).execute()
        
        return jsonify({
            'status': 'success',
            'data': result.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@expenses_bp.route('', methods=['POST'])
@token_required
def create_expense(current_user):
    """
    Create a new expense
    
    Request Body:
        {
            "category_id": "uuid",
            "amount": 100.50,
            "currency": "USD" (optional),
            "expense_date": "2025-10-04",
            "description": "Lunch meeting",
            "receipt_url": "https://..." (optional)
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['category_id', 'amount', 'expense_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate amount
        try:
            amount = float(data['amount'])
            if amount <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'message': 'Amount must be a positive number'
            }), 400
        
        # Validate date format
        try:
            datetime.strptime(data['expense_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        supabase = get_supabase_client()
        
        # Verify category exists and belongs to company
        category_result = supabase.table('categories').select('*').eq('id', data['category_id']).eq('company_id', current_user['company_id']).execute()
        
        if not category_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Category not found'
            }), 404
        
        # Create expense
        expense_data = {
            'user_id': current_user['user_id'],
            'company_id': current_user['company_id'],
            'category_id': data['category_id'],
            'amount': amount,
            'currency': data.get('currency', 'USD'),
            'expense_date': data['expense_date'],
            'description': data.get('description', ''),
            'receipt_url': data.get('receipt_url'),
            'status': 'draft'
        }
        
        result = supabase.table('expenses').insert(expense_data).execute()
        
        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create expense'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Expense created successfully',
            'data': result.data[0]
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@expenses_bp.route('/<expense_id>', methods=['GET'])
@token_required
def get_expense(current_user, expense_id):
    """
    Get expense details by ID
    """
    try:
        supabase = get_supabase_client()
        
        # Get expense with joined data
        result = supabase.table('expenses').select('*, users!expenses_user_id_fkey(name, email), categories(name)').eq('id', expense_id).eq('company_id', current_user['company_id']).execute()
        
        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'Expense not found'
            }), 404
        
        expense = result.data[0]
        
        # Check permissions
        if current_user['role'] == 'employee' and expense['user_id'] != current_user['user_id']:
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        return jsonify({
            'status': 'success',
            'data': expense
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@expenses_bp.route('/<expense_id>', methods=['PUT'])
@token_required
def update_expense(current_user, expense_id):
    """
    Update expense details
    - Users can update their own expenses (if status is draft)
    - Admins and managers can update any expense
    """
    try:
        data = request.get_json()
        supabase = get_supabase_client()
        
        # Get existing expense
        existing_result = supabase.table('expenses').select('*').eq('id', expense_id).eq('company_id', current_user['company_id']).execute()
        
        if not existing_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Expense not found'
            }), 404
        
        existing_expense = existing_result.data[0]
        
        # Check permissions
        is_owner = existing_expense['user_id'] == current_user['user_id']
        is_admin_or_manager = current_user['role'] in ['admin', 'manager']
        
        if not (is_owner or is_admin_or_manager):
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        # Employees can only edit draft expenses
        if is_owner and not is_admin_or_manager and existing_expense['status'] != 'draft':
            return jsonify({
                'status': 'error',
                'message': 'Can only edit expenses in draft status'
            }), 403
        
        # Build update data
        update_data = {}
        
        if 'category_id' in data:
            # Verify category exists
            category_result = supabase.table('categories').select('*').eq('id', data['category_id']).eq('company_id', current_user['company_id']).execute()
            if not category_result.data:
                return jsonify({
                    'status': 'error',
                    'message': 'Category not found'
                }), 404
            update_data['category_id'] = data['category_id']
        
        if 'amount' in data:
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    raise ValueError()
                update_data['amount'] = amount
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': 'Amount must be a positive number'
                }), 400
        
        if 'expense_date' in data:
            try:
                datetime.strptime(data['expense_date'], '%Y-%m-%d')
                update_data['expense_date'] = data['expense_date']
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        if 'description' in data:
            update_data['description'] = data['description']
        
        if 'receipt_url' in data:
            update_data['receipt_url'] = data['receipt_url']
        
        if 'currency' in data:
            update_data['currency'] = data['currency']
        
        # Only admins/managers can change status directly
        if 'status' in data and is_admin_or_manager:
            if validate_expense_status(data['status']):
                update_data['status'] = data['status']
        
        if not update_data:
            return jsonify({
                'status': 'error',
                'message': 'No valid fields to update'
            }), 400
        
        # Update expense
        result = supabase.table('expenses').update(update_data).eq('id', expense_id).execute()
        
        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update expense'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Expense updated successfully',
            'data': result.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@expenses_bp.route('/<expense_id>', methods=['DELETE'])
@token_required
def delete_expense(current_user, expense_id):
    """
    Delete expense
    - Users can delete their own draft expenses
    - Admins can delete any expense
    """
    try:
        supabase = get_supabase_client()
        
        # Get expense
        existing_result = supabase.table('expenses').select('*').eq('id', expense_id).eq('company_id', current_user['company_id']).execute()
        
        if not existing_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Expense not found'
            }), 404
        
        expense = existing_result.data[0]
        
        # Check permissions
        is_owner = expense['user_id'] == current_user['user_id']
        is_admin = current_user['role'] == 'admin'
        
        if not (is_owner or is_admin):
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        # Employees can only delete draft expenses
        if is_owner and not is_admin and expense['status'] != 'draft':
            return jsonify({
                'status': 'error',
                'message': 'Can only delete expenses in draft status'
            }), 403
        
        # Delete expense
        supabase.table('expenses').delete().eq('id', expense_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Expense deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@expenses_bp.route('/<expense_id>/submit', methods=['POST'])
@token_required
def submit_expense(current_user, expense_id):
    """
    Submit expense for approval
    Changes status from draft to submitted
    """
    try:
        supabase = get_supabase_client()
        
        # Get expense
        existing_result = supabase.table('expenses').select('*').eq('id', expense_id).eq('company_id', current_user['company_id']).execute()
        
        if not existing_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Expense not found'
            }), 404
        
        expense = existing_result.data[0]
        
        # Check if user owns the expense
        if expense['user_id'] != current_user['user_id']:
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        # Check if already submitted
        if expense['status'] != 'draft':
            return jsonify({
                'status': 'error',
                'message': f'Expense is already {expense["status"]}'
            }), 400
        
        # Update status to submitted
        result = supabase.table('expenses').update({
            'status': 'submitted',
            'submitted_at': datetime.utcnow().isoformat()
        }).eq('id', expense_id).execute()
        
        # TODO: Create approval requests based on approval rules
        # This will be implemented when we add the approvals route
        
        return jsonify({
            'status': 'success',
            'message': 'Expense submitted successfully',
            'data': result.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
