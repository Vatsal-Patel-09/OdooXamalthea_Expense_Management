"""
Approvals Routes
Handles expense approval workflow
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from utils.auth import token_required
from utils.currency import convert_to_company_currency
from datetime import datetime

approvals_bp = Blueprint('approvals', __name__)


@approvals_bp.route('', methods=['GET'])
@token_required
def list_approvals(current_user):
    """
    Get list of approvals (for managers/admins)
    
    GET /api/approvals?status=pending&expense_id=123
    
    Query Parameters:
    - status: Filter by status (pending, approved, rejected)
    - expense_id: Filter by expense
    
    Response:
    {
        "success": true,
        "message": "Approvals retrieved successfully",
        "data": [...]
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        user_id = current_user['user_id']
        role = current_user['role']
        
        # Only managers and admins can see approvals
        if role not in ['manager', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Unauthorized: Only managers and admins can access approvals'
            }), 403
        
        # Base query - get approvals for this user
        query = supabase.table('approvals').select(
            '''
            *, 
            expense:expenses(
                id, amount, currency, expense_date, description, status, receipt_url, paid_by,
                category:categories(name),
                user:users(name, email)
            ),
            approver:users!approvals_approver_user_id_fkey(id, name, email),
            rule:approval_rules(name, approval_percentage, is_sequential)
            '''
        ).eq('approver_user_id', user_id)
        
        # Apply filters
        status = request.args.get('status')
        if status:
            query = query.eq('status', status)
        
        expense_id = request.args.get('expense_id')
        if expense_id:
            query = query.eq('expense_id', expense_id)
        
        # Order by created date (most recent first)
        query = query.order('created_at', desc=True)
        
        result = query.execute()
        
        # Add currency conversion for each approval
        approvals_with_conversion = []
        for approval in result.data:
            if approval.get('expense'):
                expense = approval['expense']
                
                # Get company info for currency
                company_result = supabase.table('companies').select('currency').eq('id', company_id).execute()
                company_currency = company_result.data[0]['currency'] if company_result.data else 'USD'
                
                # Convert amount if needed
                conversion = convert_to_company_currency(
                    float(expense['amount']),
                    expense['currency'],
                    company_currency
                )
                
                approval['expense']['converted_amount'] = conversion.get('converted_amount')
                approval['expense']['company_currency'] = company_currency
                approval['expense']['conversion_rate'] = conversion.get('exchange_rate')
            
            approvals_with_conversion.append(approval)
        
        return jsonify({
            'success': True,
            'message': 'Approvals retrieved successfully',
            'data': approvals_with_conversion
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve approvals: {str(e)}'
        }), 500


@approvals_bp.route('/<approval_id>/approve', methods=['POST'])
@token_required
def approve_expense(current_user, approval_id):
    """
    Approve an expense
    
    POST /api/approvals/:id/approve
    Request Body:
    {
        "comments": "Approved for business trip"
    }
    
    Response:
    {
        "success": true,
        "message": "Expense approved successfully",
        "data": {...}
    }
    """
    try:
        data = request.get_json() or {}
        comments = data.get('comments', '')
        
        supabase = get_supabase_client()
        user_id = current_user['user_id']
        role = current_user['role']
        
        # Only managers and admins can approve
        if role not in ['manager', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Unauthorized: Only managers and admins can approve expenses'
            }), 403
        
        # Get approval record
        approval_result = supabase.table('approvals').select(
            '*, expense:expenses(id, status), rule:approval_rules(approval_percentage, is_sequential)'
        ).eq('id', approval_id).eq('approver_user_id', user_id).execute()
        
        if not approval_result.data:
            return jsonify({
                'success': False,
                'message': 'Approval not found or not assigned to you'
            }), 404
        
        approval = approval_result.data[0]
        expense = approval['expense']
        
        # Check if expense is in submitted status
        if expense['status'] != 'submitted':
            return jsonify({
                'success': False,
                'message': f'Cannot approve expense with status: {expense["status"]}'
            }), 400
        
        # Check if already approved/rejected
        if approval['status'] != 'pending':
            return jsonify({
                'success': False,
                'message': f'Approval already {approval["status"]}'
            }), 400
        
        # Update approval record
        supabase.table('approvals').update({
            'status': 'approved',
            'comments': comments,
            'approved_at': datetime.now().isoformat()
        }).eq('id', approval_id).execute()
        
        # Check if all required approvals are met
        expense_id = approval['expense_id']
        rule_id = approval['rule_id']
        
        # Get all approvals for this expense
        all_approvals = supabase.table('approvals').select('status').eq(
            'expense_id', expense_id
        ).eq('rule_id', rule_id).execute()
        
        total_approvals = len(all_approvals.data)
        approved_count = len([a for a in all_approvals.data if a['status'] == 'approved'])
        
        # Calculate approval percentage
        rule = approval['rule']
        required_percentage = float(rule['approval_percentage'])
        current_percentage = (approved_count / total_approvals) * 100 if total_approvals > 0 else 0
        
        # If required percentage met, approve the expense
        if current_percentage >= required_percentage:
            supabase.table('expenses').update({
                'status': 'approved'
            }).eq('id', expense_id).execute()
            
            message = f'Expense approved successfully (all approvals met: {approved_count}/{total_approvals})'
        else:
            message = f'Approval recorded ({approved_count}/{total_approvals} approved, {required_percentage}% required)'
        
        # Get updated approval
        updated_approval = supabase.table('approvals').select(
            '*, expense:expenses(*, category:categories(name), user:users(name, email))'
        ).eq('id', approval_id).execute()
        
        return jsonify({
            'success': True,
            'message': message,
            'data': updated_approval.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to approve expense: {str(e)}'
        }), 500


@approvals_bp.route('/<approval_id>/reject', methods=['POST'])
@token_required
def reject_expense(current_user, approval_id):
    """
    Reject an expense
    
    POST /api/approvals/:id/reject
    Request Body:
    {
        "comments": "Missing required documentation"
    }
    
    Response:
    {
        "success": true,
        "message": "Expense rejected successfully",
        "data": {...}
    }
    """
    try:
        data = request.get_json() or {}
        comments = data.get('comments', '')
        
        if not comments:
            return jsonify({
                'success': False,
                'message': 'Comments are required when rejecting an expense'
            }), 400
        
        supabase = get_supabase_client()
        user_id = current_user['user_id']
        role = current_user['role']
        
        # Only managers and admins can reject
        if role not in ['manager', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Unauthorized: Only managers and admins can reject expenses'
            }), 403
        
        # Get approval record
        approval_result = supabase.table('approvals').select(
            '*, expense:expenses(id, status)'
        ).eq('id', approval_id).eq('approver_user_id', user_id).execute()
        
        if not approval_result.data:
            return jsonify({
                'success': False,
                'message': 'Approval not found or not assigned to you'
            }), 404
        
        approval = approval_result.data[0]
        expense = approval['expense']
        
        # Check if expense is in submitted status
        if expense['status'] != 'submitted':
            return jsonify({
                'success': False,
                'message': f'Cannot reject expense with status: {expense["status"]}'
            }), 400
        
        # Check if already approved/rejected
        if approval['status'] != 'pending':
            return jsonify({
                'success': False,
                'message': f'Approval already {approval["status"]}'
            }), 400
        
        # Update approval record
        supabase.table('approvals').update({
            'status': 'rejected',
            'comments': comments,
            'approved_at': datetime.now().isoformat()
        }).eq('id', approval_id).execute()
        
        # Reject the expense (one rejection rejects the whole expense)
        supabase.table('expenses').update({
            'status': 'rejected'
        }).eq('id', approval['expense_id']).execute()
        
        # Get updated approval
        updated_approval = supabase.table('approvals').select(
            '*, expense:expenses(*, category:categories(name), user:users(name, email))'
        ).eq('id', approval_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Expense rejected successfully',
            'data': updated_approval.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to reject expense: {str(e)}'
        }), 500


@approvals_bp.route('/stats', methods=['GET'])
@token_required
def get_approval_stats(current_user):
    """
    Get approval statistics for current user (manager/admin)
    
    GET /api/approvals/stats
    
    Response:
    {
        "success": true,
        "message": "Statistics retrieved successfully",
        "data": {
            "total_pending": 5,
            "total_approved": 10,
            "total_rejected": 2
        }
    }
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user['user_id']
        role = current_user['role']
        
        if role not in ['manager', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Unauthorized: Only managers and admins can access approval statistics'
            }), 403
        
        # Get all approvals for this user
        result = supabase.table('approvals').select('status').eq('approver_user_id', user_id).execute()
        
        approvals = result.data
        
        stats = {
            'total_pending': len([a for a in approvals if a['status'] == 'pending']),
            'total_approved': len([a for a in approvals if a['status'] == 'approved']),
            'total_rejected': len([a for a in approvals if a['status'] == 'rejected']),
            'total_approvals': len(approvals)
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
