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
    # Prefer Service Key for backend operations to bypass RLS, fall back to Anon Key
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY (or SUPABASE_SERVICE_KEY) must be set")
    
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
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Starting upload for file: {filename}")
        
        # Get Supabase client
        supabase = get_supabase_client()
        bucket = "opg-images"
        logger.info(f"Supabase client initialized, bucket: {bucket}")
        
        # Reset file pointer to beginning
        file.seek(0)
        file_content = file.read()
        logger.info(f"File read successfully, size: {len(file_content)} bytes")
        
        # Upload file to Supabase Storage
        try:
            logger.info(f"Attempting to upload to Supabase storage bucket '{bucket}'")
            res = supabase.storage.from_(bucket).upload(
                file=file_content,
                path=filename,
                file_options={"content-type": file.content_type}
            )
            logger.info(f"Upload response received: {type(res)}")
            logger.info(f"Upload response: {res}")
        except Exception as upload_error:
            logger.error(f"Upload to Supabase failed: {str(upload_error)}")
            logger.error(f"Upload error type: {type(upload_error)}")
            raise Exception(f"Failed to upload file to Supabase storage: {str(upload_error)}")
        
        # Generate signed URL that expires in 1 year (for permanent access)
        # This is needed when RLS (Row Level Security) is enabled
        try:
            logger.info("Generating signed URL for uploaded file")
            expiry_time = 365 * 24 * 60 * 60  # 1 year in seconds
            signed_url_response = supabase.storage.from_(bucket).create_signed_url(filename, expiry_time)
            logger.info(f"Signed URL response type: {type(signed_url_response)}")
            logger.info(f"Signed URL response: {signed_url_response}")
            
            # Extract the signed URL from the response
            signed_url = None
            if isinstance(signed_url_response, dict):
                # Try different possible keys
                signed_url = (signed_url_response.get("signedURL") or 
                             signed_url_response.get("signedUrl") or
                             signed_url_response.get("signed_url") or
                             signed_url_response.get("url"))
                logger.info(f"Extracted signed URL from dict: {signed_url}")
            elif isinstance(signed_url_response, str):
                signed_url = signed_url_response
                logger.info(f"Signed URL is string: {signed_url}")
            
            if signed_url:
                logger.info(f"Successfully generated signed URL for {filename}")
                return signed_url
            else:
                logger.warning(f"Could not extract signed URL from response, falling back to public URL")
                # Fallback to public URL
                public_url = supabase.storage.from_(bucket).get_public_url(filename)
                logger.info(f"Generated public URL: {public_url}")
                return public_url
                
        except Exception as url_error:
            logger.error(f"Failed to generate signed URL: {str(url_error)}")
            logger.error(f"Attempting fallback to public URL")
            try:
                public_url = supabase.storage.from_(bucket).get_public_url(filename)
                logger.info(f"Fallback public URL generated: {public_url}")
                return public_url
            except Exception as public_url_error:
                logger.error(f"Failed to generate public URL: {str(public_url_error)}")
                raise Exception(f"Failed to generate URL for uploaded file: {str(url_error)}")
        
    except Exception as e:
        logger.error(f"Upload process failed: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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