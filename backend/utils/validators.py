"""
Validation utilities for request data
"""

import re
from typing import Optional

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    Password must be at least 8 characters
    
    Args:
        password: Password to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    return True, None

def validate_role(role: str) -> bool:
    """
    Validate user role
    
    Args:
        role: User role
    
    Returns:
        bool: True if valid role
    """
    valid_roles = ['admin', 'manager', 'employee']
    return role in valid_roles

def validate_expense_status(status: str) -> bool:
    """
    Validate expense status
    
    Args:
        status: Expense status
    
    Returns:
        bool: True if valid status
    """
    valid_statuses = ['draft', 'submitted', 'approved', 'rejected']
    return status in valid_statuses

def validate_approval_status(status: str) -> bool:
    """
    Validate approval status
    
    Args:
        status: Approval status
    
    Returns:
        bool: True if valid status
    """
    valid_statuses = ['pending', 'approved', 'rejected']
    return status in valid_statuses
