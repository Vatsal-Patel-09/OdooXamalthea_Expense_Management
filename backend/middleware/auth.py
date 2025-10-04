"""
Authentication Middleware
Protects routes and verifies JWT tokens
"""

from functools import wraps
from flask import request, jsonify
from utils.jwt_helper import decode_token, get_token_from_header

def token_required(f):
    """
    Decorator to protect routes with JWT authentication
    Adds 'current_user' to kwargs with decoded token data
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Get token from header
            token = get_token_from_header()
            
            # Decode and verify token
            payload = decode_token(token)
            
            # Add user info to kwargs
            kwargs['current_user'] = payload
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated

def role_required(*allowed_roles):
    """
    Decorator to check if user has required role
    Must be used after @token_required
    
    Args:
        allowed_roles: List of allowed roles (e.g., 'admin', 'manager')
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user:
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication required'
                }), 401
            
            user_role = current_user.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'status': 'error',
                    'message': f'Access denied. Required role: {", ".join(allowed_roles)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator
