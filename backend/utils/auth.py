"""
Authentication utilities
Handles JWT token generation, validation, and password hashing
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# JWT Configuration
JWT_SECRET = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def hash_password(password: str) -> str:
    """
    Hash a password using werkzeug's security functions
    Args:
        password: Plain text password
    Returns:
        Hashed password string
    """
    return generate_password_hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash
    Args:
        password: Plain text password to verify
        password_hash: Hashed password to check against
    Returns:
        True if password matches, False otherwise
    """
    return check_password_hash(password_hash, password)

def generate_token(user_id: str, email: str, role: str, company_id: str) -> str:
    """
    Generate JWT token for authenticated user
    Args:
        user_id: User's UUID
        email: User's email
        role: User's role (admin, manager, employee)
        company_id: User's company UUID
    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'company_id': company_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    """
    Decode and verify JWT token
    Args:
        token: JWT token string
    Returns:
        Decoded payload dictionary
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def token_required(f):
    """
    Decorator to protect routes that require authentication
    Usage: @token_required on any route function
    Adds 'current_user' to the function arguments
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid token format. Use: Bearer <token>'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Authentication token is missing'
            }), 401
        
        try:
            # Decode token and get user info
            current_user = decode_token(token)
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Token validation failed: {str(e)}'
            }), 401
    
    return decorated

def admin_required(f):
    """
    Decorator to protect routes that require admin role
    Usage: @admin_required on any route function
    Must be used with @token_required
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def manager_or_admin_required(f):
    """
    Decorator to protect routes that require manager or admin role
    Usage: @manager_or_admin_required on any route function
    Must be used with @token_required
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get('role') not in ['admin', 'manager']:
            return jsonify({
                'success': False,
                'message': 'Manager or Admin access required'
            }), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated
