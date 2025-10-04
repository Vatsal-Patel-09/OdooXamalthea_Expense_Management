"""
Approval Workflow Utilities
Handles automatic approval creation when expenses are submitted
"""

from config.database import get_supabase_client
from utils.currency import convert_to_company_currency
from typing import Optional, Dict, List


def find_matching_rule(expense_id: str, company_id: str) -> Optional[Dict]:
    """
    Find the approval rule that matches an expense
    
    Priority:
    1. Rule with matching category and amount range
    2. Rule with matching category only (no amount limits)
    3. Rule with no category but matching amount range
    4. Default rule (no category, no amount limits)
    
    Args:
        expense_id: The expense ID to find a rule for
        company_id: The company ID
        
    Returns:
        Matching rule dict or None
    """
    try:
        supabase = get_supabase_client()
        
        # Get expense details
        expense_result = supabase.table('expenses').select(
            'id, category_id, amount, currency'
        ).eq('id', expense_id).execute()
        
        if not expense_result.data:
            return None
        
        expense = expense_result.data[0]
        
        # Get company currency for conversion
        company_result = supabase.table('companies').select('currency').eq('id', company_id).execute()
        company_currency = company_result.data[0]['currency'] if company_result.data else 'USD'
        
        # Convert expense amount to company currency
        conversion = convert_to_company_currency(
            float(expense['amount']),
            expense['currency'],
            company_currency
        )
        converted_amount = conversion.get('converted_amount', float(expense['amount']))
        
        # Get all active rules for the company
        rules_result = supabase.table('approval_rules').select(
            '*'
        ).eq('company_id', company_id).eq('is_active', True).order('created_at').execute()
        
        if not rules_result.data:
            return None
        
        rules = rules_result.data
        category_id = expense.get('category_id')
        
        # Priority 1: Category + Amount Range match
        for rule in rules:
            if rule.get('category_id') == category_id:
                min_amount = float(rule['min_amount']) if rule['min_amount'] is not None else 0
                max_amount = float(rule['max_amount']) if rule['max_amount'] is not None else float('inf')
                
                if min_amount <= converted_amount <= max_amount:
                    return rule
        
        # Priority 2: Category match only (no amount restrictions)
        for rule in rules:
            if rule.get('category_id') == category_id and rule['max_amount'] is None:
                return rule
        
        # Priority 3: Amount range match (no category restriction)
        for rule in rules:
            if rule.get('category_id') is None:
                min_amount = float(rule['min_amount']) if rule['min_amount'] is not None else 0
                max_amount = float(rule['max_amount']) if rule['max_amount'] is not None else float('inf')
                
                if min_amount <= converted_amount <= max_amount:
                    return rule
        
        # Priority 4: Default rule (no category, no amount limits)
        for rule in rules:
            if rule.get('category_id') is None and rule['max_amount'] is None:
                return rule
        
        return None
        
    except Exception as e:
        print(f"Error finding matching rule: {str(e)}")
        return None


def create_approval_records(expense_id: str, rule_id: str) -> bool:
    """
    Create approval records for an expense based on the rule
    
    Args:
        expense_id: The expense ID
        rule_id: The approval rule ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        # Get rule with approvers
        rule_result = supabase.table('approval_rules').select(
            '*, approvers:approval_rule_approvers(approver_user_id, order_index)'
        ).eq('id', rule_id).execute()
        
        if not rule_result.data:
            print(f"Rule not found: {rule_id}")
            return False
        
        rule = rule_result.data[0]
        approvers = rule.get('approvers', [])
        
        if not approvers:
            print(f"No approvers found for rule: {rule_id}")
            # No approvers means auto-approve
            supabase.table('expenses').update({
                'status': 'approved'
            }).eq('id', expense_id).execute()
            return True
        
        # Sort approvers by order_index (for sequential approval)
        approvers.sort(key=lambda x: x['order_index'])
        
        # Create approval records
        approval_records = []
        for approver in approvers:
            approval_records.append({
                'expense_id': expense_id,
                'rule_id': rule_id,
                'approver_user_id': approver['approver_user_id'],
                'status': 'pending',
                'order_index': approver['order_index']
            })
        
        # Insert all approval records
        supabase.table('approvals').insert(approval_records).execute()
        
        return True
        
    except Exception as e:
        print(f"Error creating approval records: {str(e)}")
        return False


def trigger_approval_workflow(expense_id: str, company_id: str) -> Dict:
    """
    Trigger the approval workflow for a submitted expense
    
    This function:
    1. Finds matching approval rule
    2. Creates approval records
    3. Updates expense status if needed
    
    Args:
        expense_id: The expense ID
        company_id: The company ID
        
    Returns:
        Dict with success status and message
    """
    try:
        # Find matching rule
        rule = find_matching_rule(expense_id, company_id)
        
        if not rule:
            # No rule found - auto-approve
            supabase = get_supabase_client()
            supabase.table('expenses').update({
                'status': 'approved'
            }).eq('id', expense_id).execute()
            
            return {
                'success': True,
                'message': 'No approval rule found - expense auto-approved',
                'auto_approved': True
            }
        
        # Create approval records
        success = create_approval_records(expense_id, rule['id'])
        
        if not success:
            return {
                'success': False,
                'message': 'Failed to create approval records'
            }
        
        return {
            'success': True,
            'message': f'Approval workflow triggered - {len(rule.get("approvers", []))} approver(s) assigned',
            'rule_name': rule['name'],
            'rule_id': rule['id']
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to trigger approval workflow: {str(e)}'
        }


def get_expense_approval_status(expense_id: str) -> Dict:
    """
    Get the approval status for an expense
    
    Args:
        expense_id: The expense ID
        
    Returns:
        Dict with approval status information
    """
    try:
        supabase = get_supabase_client()
        
        # Get all approvals for this expense
        approvals_result = supabase.table('approvals').select(
            '''
            *,
            approver:users!approvals_approver_user_id_fkey(id, name, email),
            rule:approval_rules(name, approval_percentage, is_sequential)
            '''
        ).eq('expense_id', expense_id).order('order_index').execute()
        
        if not approvals_result.data:
            return {
                'has_approvals': False,
                'message': 'No approvals required'
            }
        
        approvals = approvals_result.data
        rule = approvals[0]['rule']
        
        total = len(approvals)
        approved = len([a for a in approvals if a['status'] == 'approved'])
        rejected = len([a for a in approvals if a['status'] == 'rejected'])
        pending = len([a for a in approvals if a['status'] == 'pending'])
        
        approval_percentage = (approved / total) * 100 if total > 0 else 0
        required_percentage = float(rule['approval_percentage'])
        
        return {
            'has_approvals': True,
            'total_approvals': total,
            'approved_count': approved,
            'rejected_count': rejected,
            'pending_count': pending,
            'approval_percentage': approval_percentage,
            'required_percentage': required_percentage,
            'is_sequential': rule['is_sequential'],
            'rule_name': rule['name'],
            'approvals': approvals
        }
        
    except Exception as e:
        return {
            'has_approvals': False,
            'message': f'Error retrieving approval status: {str(e)}'
        }
