import os
from supabase import create_client, Client
from datetime import datetime, timedelta

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.
    
    Returns:
        Client: Supabase client instance
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    return create_client(url, key)

def upload_image(file, filename: str) -> str:
    """
    Upload an OPG image to Supabase storage and return the public URL.
    
    Args:
        file: File object to upload
        filename (str): Name to give the file in storage
        
    Returns:
        str: Public URL of the uploaded file
        
    Raises:
        Exception: If upload fails
    """
    try:
        supabase = get_supabase_client()
        bucket = "opg-images"
        
        # Reset file pointer to beginning
        file.seek(0)
        
        # Upload file
        res = supabase.storage.from_(bucket).upload(
            file=file.read(),
            path=filename,
            file_options={"content-type": file.content_type}
        )
        
        # Check for errors
        if hasattr(res, 'error') and res.error:
            raise Exception(f"Upload failed: {res.error}")
        
        # Generate signed URL that expires in 1 year (for permanent access)
        # This is needed when RLS (Row Level Security) is enabled
        expiry_time = int((datetime.now() + timedelta(days=365)).timestamp())
        signed_url_data = supabase.storage.from_(bucket).create_signed_url(filename, expiry_time)
        
        # Properly extract the signed URL from the response
        if isinstance(signed_url_data, dict):
            # Newer versions of supabase return a dict
            return signed_url_data.get("signedURL") or str(signed_url_data)
        else:
            # Older versions might return the URL directly
            return str(signed_url_data)
        
    except Exception as e:
        raise Exception(f"Failed to upload image to Supabase: {str(e)}")

def delete_image(filename: str) -> bool:
    """
    Delete an OPG image from Supabase storage.
    
    Args:
        filename (str): Name of the file to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        Exception: If deletion fails
    """
    try:
        supabase = get_supabase_client()
        bucket = "opg-images"
        
        # Delete file
        res = supabase.storage.from_(bucket).remove([filename])
        
        # Check for errors
        if hasattr(res, 'error') and res.error:
            raise Exception(f"Deletion failed: {res.error}")
            
        return True
        
    except Exception as e:
        raise Exception(f"Failed to delete image from Supabase: {str(e)}")