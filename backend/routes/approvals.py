"""
Approval Management Routes
Handles approval workflows for expenses
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from middleware.auth import token_required, role_required
from datetime import datetime

approvals_bp = Blueprint('approvals', __name__)

@approvals_bp.route('', methods=['GET'])
@token_required
def list_approvals(current_user):
    """
    List approval requests
    - Shows pending approvals assigned to current user
    - Admins can see all approvals
    
    Query Parameters:
        status: Filter by status (pending, approved, rejected)
        expense_id: Filter by expense
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user['user_id']
        user_role = current_user['role']
        
        # Build query
        query = supabase.table('approvals').select('*, expenses(*, users!expenses_user_id_fkey(name, email), categories(name))')
        
        # Role-based filtering
        if user_role != 'admin':
            # Non-admins see only their approval requests
            query = query.eq('approver_id', user_id)
        else:
            # Admins see all approvals in their company
            query = query.eq('expenses.company_id', current_user['company_id'])
        
        # Apply filters
        status = request.args.get('status')
        if status:
            query = query.eq('status', status)
        
        expense_id = request.args.get('expense_id')
        if expense_id:
            query = query.eq('expense_id', expense_id)
        
        result = query.order('created_at', desc=True).execute()
        
        return jsonify({
            'status': 'success',
            'data': result.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@approvals_bp.route('/<approval_id>', methods=['GET'])
@token_required
def get_approval(current_user, approval_id):
    """
    Get approval details by ID
    """
    try:
        supabase = get_supabase_client()
        
        # Get approval with expense details
        result = supabase.table('approvals').select('*, expenses(*, users!expenses_user_id_fkey(name, email), categories(name))').eq('id', approval_id).execute()
        
        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'Approval not found'
            }), 404
        
        approval = result.data[0]
        
        # Check permissions
        if current_user['role'] != 'admin' and approval['approver_id'] != current_user['user_id']:
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        return jsonify({
            'status': 'success',
            'data': approval
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@approvals_bp.route('/<approval_id>/approve', methods=['POST'])
@token_required
def approve_expense(current_user, approval_id):
    """
    Approve an expense
    
    Request Body:
        {
            "comments": "Approved" (optional)
        }
    """
    try:
        data = request.get_json() or {}
        supabase = get_supabase_client()
        
        # Get approval
        approval_result = supabase.table('approvals').select('*, expenses(*)').eq('id', approval_id).execute()
        
        if not approval_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Approval request not found'
            }), 404
        
        approval = approval_result.data[0]
        
        # Check if user is the approver or admin
        if current_user['user_id'] != approval['approver_id'] and current_user['role'] != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        # Check if already processed
        if approval['status'] != 'pending':
            return jsonify({
                'status': 'error',
                'message': f'Approval already {approval["status"]}'
            }), 400
        
        # Update approval status
        approval_update = {
            'status': 'approved',
            'comments': data.get('comments', ''),
            'responded_at': datetime.utcnow().isoformat()
        }
        
        supabase.table('approvals').update(approval_update).eq('id', approval_id).execute()
        
        # Check if all approvals for this expense are approved
        expense_id = approval['expense_id']
        all_approvals = supabase.table('approvals').select('*').eq('expense_id', expense_id).execute()
        
        all_approved = all(a['status'] == 'approved' for a in all_approvals.data)
        
        if all_approved:
            # Update expense status to approved
            supabase.table('expenses').update({'status': 'approved'}).eq('id', expense_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Expense approved successfully',
            'expense_fully_approved': all_approved
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@approvals_bp.route('/<approval_id>/reject', methods=['POST'])
@token_required
def reject_expense(current_user, approval_id):
    """
    Reject an expense
    
    Request Body:
        {
            "comments": "Reason for rejection" (required)
        }
    """
    try:
        data = request.get_json() or {}
        
        # Require comments for rejection
        if not data.get('comments'):
            return jsonify({
                'status': 'error',
                'message': 'Comments are required when rejecting an expense'
            }), 400
        
        supabase = get_supabase_client()
        
        # Get approval
        approval_result = supabase.table('approvals').select('*, expenses(*)').eq('id', approval_id).execute()
        
        if not approval_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Approval request not found'
            }), 404
        
        approval = approval_result.data[0]
        
        # Check if user is the approver or admin
        if current_user['user_id'] != approval['approver_id'] and current_user['role'] != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        # Check if already processed
        if approval['status'] != 'pending':
            return jsonify({
                'status': 'error',
                'message': f'Approval already {approval["status"]}'
            }), 400
        
        # Update approval status
        approval_update = {
            'status': 'rejected',
            'comments': data['comments'],
            'responded_at': datetime.utcnow().isoformat()
        }
        
        supabase.table('approvals').update(approval_update).eq('id', approval_id).execute()
        
        # Update expense status to rejected
        expense_id = approval['expense_id']
        supabase.table('expenses').update({'status': 'rejected'}).eq('id', expense_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Expense rejected successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@approvals_bp.route('/expense/<expense_id>', methods=['POST'])
@token_required
@role_required('admin', 'manager')
def create_approval_request(current_user, expense_id):
    """
    Create approval request for an expense (Admin/Manager only)
    Typically called when expense is submitted
    
    Request Body:
        {
            "approver_id": "uuid" (required)
        }
    """
    try:
        data = request.get_json()
        
        if not data.get('approver_id'):
            return jsonify({
                'status': 'error',
                'message': 'Approver ID is required'
            }), 400
        
        supabase = get_supabase_client()
        
        # Verify expense exists
        expense_result = supabase.table('expenses').select('*').eq('id', expense_id).eq('company_id', current_user['company_id']).execute()
        
        if not expense_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Expense not found'
            }), 404
        
        # Verify approver exists and is in same company
        approver_result = supabase.table('users').select('*').eq('id', data['approver_id']).eq('company_id', current_user['company_id']).execute()
        
        if not approver_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Approver not found'
            }), 404
        
        # Check if approval already exists
        existing_approval = supabase.table('approvals').select('*').eq('expense_id', expense_id).eq('approver_id', data['approver_id']).execute()
        
        if existing_approval.data:
            return jsonify({
                'status': 'error',
                'message': 'Approval request already exists for this approver'
            }), 409
        
        # Create approval request
        approval_data = {
            'expense_id': expense_id,
            'approver_id': data['approver_id'],
            'status': 'pending'
        }
        
        result = supabase.table('approvals').insert(approval_data).execute()
        
        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create approval request'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Approval request created successfully',
            'data': result.data[0]
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
