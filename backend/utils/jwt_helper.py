"""
JWT Token Helper Functions
Handles JWT token generation and verification
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# JWT Secret from environment
JWT_SECRET = os.getenv('SECRET_KEY', 'dev-secret-key')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def generate_token(user_id: str, email: str, role: str, company_id: str) -> str:
    """
    Generate JWT token for authenticated user
    
    Args:
        user_id: User UUID
        email: User email
        role: User role (admin, manager, employee)
        company_id: Company UUID
    
    Returns:
        str: JWT token
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
        dict: Decoded payload
    
    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def get_token_from_header() -> str:
    """
    Extract JWT token from Authorization header
    
    Returns:
        str: JWT token
    
    Raises:
        Exception: If token is missing or invalid format
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        raise Exception("Authorization header is missing")
    
    parts = auth_header.split()
    
    if parts[0].lower() != 'bearer':
        raise Exception("Authorization header must start with Bearer")
    
    if len(parts) == 1:
        raise Exception("Token not found")
    
    if len(parts) > 2:
        raise Exception("Authorization header must be Bearer token")
    
    return parts[1]
