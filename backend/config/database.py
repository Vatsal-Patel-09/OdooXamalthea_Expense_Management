"""
Supabase Database Configuration
Handles connection to Supabase PostgreSQL database
"""

import os
from supabase import create_client, Client

# NOTE: Environment variables are loaded in app.py before this module is imported
# This ensures proper order of initialization

# Initialize Supabase client
supabase: Client = None

def get_supabase_url():
    """Get Supabase URL from environment"""
    return os.getenv('SUPABASE_URL')

def get_supabase_key():
    """Get Supabase anon key from environment"""
    return os.getenv('SUPABASE_KEY')

def get_supabase_service_key():
    """Get Supabase service role key from environment"""
    return os.getenv('SUPABASE_SERVICE_KEY')

def get_supabase_client() -> Client:
    """
    Get Supabase client instance (uses service role key to bypass RLS)
    Since we're handling auth in Flask with JWT, we use service role key
    Returns:
        Client: Supabase client instance
    """
    global supabase
    
    if supabase is None:
        url = get_supabase_url()
        # Use service role key instead of anon key to bypass RLS policies
        key = get_supabase_service_key()
        
        if not url or not key:
            raise ValueError("Supabase URL and SERVICE_KEY must be set in environment variables")
        
        try:
            # Create client using service role key (bypasses RLS)
            supabase = create_client(
                supabase_url=url,
                supabase_key=key
            )
        except Exception as e:
            raise
    
    return supabase

def get_supabase_admin_client() -> Client:
    """
    Get Supabase admin client (for admin operations with service role key)
    Returns:
        Client: Supabase admin client instance
    """
    url = get_supabase_url()
    service_key = get_supabase_service_key()
    
    if not url or not service_key:
        raise ValueError("Supabase URL and SERVICE_KEY must be set in environment variables")
    
    return create_client(
        supabase_url=url,
        supabase_key=service_key
    )

def test_connection() -> dict:
    """
    Test database connection
    Returns:
        dict: Connection test result
    """
    try:
        url = get_supabase_url()
        key = get_supabase_service_key()
        
        # Check if credentials are set
        if not url or url == 'your-supabase-url-here':
            return {
                'success': False,
                'message': 'Supabase URL not configured properly',
                'url': url
            }
        
        if not key or key == 'your-service-role-key-here':
            return {
                'success': False,
                'message': 'Supabase SERVICE_KEY not configured properly',
                'url': url
            }
        
        client = get_supabase_client()
        # Try to query companies table (it should exist even if empty)
        response = client.table('companies').select("count", count='exact').execute()
        
        return {
            'success': True,
            'message': 'Successfully connected to Supabase',
            'url': url
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to connect to Supabase: {str(e)}',
            'url': url if 'url' in locals() else 'unknown',
            'error_type': type(e).__name__
        }
