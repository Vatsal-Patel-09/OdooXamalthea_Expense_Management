"""
Supabase Database Configuration
Handles connection to Supabase PostgreSQL database
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Initialize Supabase client
supabase: Client = None

def get_supabase_client() -> Client:
    """
    Get Supabase client instance (for regular operations with anon key)
    Returns:
        Client: Supabase client instance
    """
    global supabase
    
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase URL and KEY must be set in environment variables")
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    return supabase

def get_supabase_admin_client() -> Client:
    """
    Get Supabase admin client (for admin operations with service role key)
    Returns:
        Client: Supabase admin client instance
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError("Supabase URL and SERVICE_KEY must be set in environment variables")
    
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def test_connection() -> dict:
    """
    Test database connection
    Returns:
        dict: Connection test result
    """
    try:
        client = get_supabase_client()
        # Try to query companies table (it should exist even if empty)
        response = client.table('companies').select("count", count='exact').execute()
        
        return {
            'success': True,
            'message': 'Successfully connected to Supabase',
            'url': SUPABASE_URL
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to connect to Supabase: {str(e)}',
            'url': SUPABASE_URL
        }
