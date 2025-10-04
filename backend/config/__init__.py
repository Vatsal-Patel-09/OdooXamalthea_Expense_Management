"""
Config package initialization
"""
from .database import get_supabase_client, get_supabase_admin_client, test_connection

__all__ = ['get_supabase_client', 'get_supabase_admin_client', 'test_connection']
