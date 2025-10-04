"""
File Upload Routes
Handles file uploads to Supabase Storage (receipts, documents, etc.)
"""

from flask import Blueprint, request, jsonify
from config.database import get_supabase_client
from utils.auth import token_required
import os
import uuid
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

# Allowed file extensions for receipts
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    """
    Upload file to Supabase Storage
    
    POST /api/upload
    Content-Type: multipart/form-data
    
    Form Data:
    - file: File to upload (image or PDF)
    - folder: Optional folder name (default: 'receipts')
    
    Response:
    {
        "success": true,
        "message": "File uploaded successfully",
        "data": {
            "url": "https://...storage.supabase.co/.../file.jpg",
            "path": "receipts/uuid-filename.jpg",
            "filename": "original-filename.jpg",
            "size": 123456
        }
    }
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'message': f'File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB'
            }), 400
        
        # Generate unique filename
        original_filename = file.filename
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Get folder from request or use default
        folder = request.form.get('folder', 'receipts')
        
        # Create full path with user company ID for organization
        company_id = current_user['company_id']
        user_id = current_user['user_id']
        timestamp = datetime.now().strftime('%Y-%m')
        
        file_path = f"{folder}/{company_id}/{timestamp}/{unique_filename}"
        
        # Read file data
        file_data = file.read()
        
        # Upload to Supabase Storage
        supabase = get_supabase_client()
        
        # Upload file (Supabase Storage bucket should be named 'receipts')
        storage = supabase.storage.from_('receipts')
        response = storage.upload(file_path, file_data, {
            'content-type': file.content_type,
            'upsert': 'false'
        })
        
        # Get public URL
        public_url = storage.get_public_url(file_path)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'data': {
                'url': public_url,
                'path': file_path,
                'filename': original_filename,
                'size': file_size,
                'uploaded_by': user_id,
                'uploaded_at': datetime.now().isoformat()
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'File upload failed: {str(e)}'
        }), 500


@upload_bp.route('/upload/<path:file_path>', methods=['DELETE'])
@token_required
def delete_file(current_user, file_path):
    """
    Delete file from Supabase Storage
    
    DELETE /api/upload/<file_path>
    
    Response:
    {
        "success": true,
        "message": "File deleted successfully"
    }
    """
    try:
        supabase = get_supabase_client()
        company_id = current_user['company_id']
        
        # Security check: Ensure file belongs to user's company
        if not file_path.startswith(f"receipts/{company_id}/"):
            return jsonify({
                'success': False,
                'message': 'Unauthorized: File does not belong to your company'
            }), 403
        
        # Delete from Supabase Storage
        storage = supabase.storage.from_('receipts')
        storage.remove([file_path])
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'File deletion failed: {str(e)}'
        }), 500


@upload_bp.route('/upload/validate', methods=['POST'])
@token_required
def validate_file(current_user):
    """
    Validate file without uploading (check size, type, etc.)
    
    POST /api/upload/validate
    Request Body:
    {
        "filename": "receipt.jpg",
        "size": 123456
    }
    
    Response:
    {
        "success": true,
        "message": "File is valid",
        "data": {
            "valid": true,
            "filename": "receipt.jpg",
            "size": 123456,
            "allowed": true
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'filename' not in data or 'size' not in data:
            return jsonify({
                'success': False,
                'message': 'filename and size are required'
            }), 400
        
        filename = data['filename']
        size = int(data['size'])
        
        # Validate extension
        is_allowed = allowed_file(filename)
        
        # Validate size
        size_ok = size <= MAX_FILE_SIZE
        
        # Build response
        validation = {
            'valid': is_allowed and size_ok,
            'filename': filename,
            'size': size,
            'allowed_extension': is_allowed,
            'size_ok': size_ok,
            'max_size': MAX_FILE_SIZE,
            'allowed_extensions': list(ALLOWED_EXTENSIONS)
        }
        
        if not validation['valid']:
            return jsonify({
                'success': False,
                'message': 'File validation failed',
                'data': validation
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'File is valid',
            'data': validation
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Validation failed: {str(e)}'
        }), 500
