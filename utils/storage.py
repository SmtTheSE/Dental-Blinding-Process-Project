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
        
        # Get Supabase client (only used for generating signed URL later if needed, or we can just use env vars)
        # We need url and key for direct HTTP request
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
             raise ValueError("SUPABASE_URL and SUPABASE_KEY (or SUPABASE_SERVICE_KEY) must be set")

        supabase = get_supabase_client()
        bucket = "opg-images"
        logger.info(f"Supabase client initialized, bucket: {bucket}")
        
        # Reset file pointer to beginning
        file.seek(0)
        file_content = file.read()
        logger.info(f"File read successfully, size: {len(file_content)} bytes")
        
        # Upload file to Supabase Storage using direct HTTP request to avoid SDK issues
        # The SDK (storage3) seems to have issues with file handling on Vercel (Errno 16 Busy)
        import requests
        
        project_id = url.split("://")[1].split(".")[0]
        storage_url = f"{url}/storage/v1/object/{bucket}/{filename}"
        
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": file.content_type,
            "x-upsert": "true"  # Force overwrite if file exists
        }
        
        logger.info(f"Uploading via direct HTTP to: {storage_url.split('?')[0]}")
        
        # Retry logic for HTTP request
        max_retries = 3
        retry_delay = 1
        
        import time
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    storage_url,
                    data=file_content,
                    headers=headers,
                    timeout=30 
                )
                
                if response.status_code in (200, 201):
                    logger.info(f"Upload successful. Status: {response.status_code}")
                    break
                elif response.status_code == 409:
                    logger.warning("File already exists (409). Treating as success/overwrite.")
                    # If we want to overwrite, we should use UPSERT or just accept it's there
                    # Supabase storage default is often not upsert unless specified. 
                    # But for now, if it exists, we can treat as success.
                    # Or better: let's try to UPSERT by adding x-upsert header if needed, 
                    # but simple upload is fine. If 409, it means it's there.
                    break
                else:
                    logger.error(f"Upload failed with status {response.status_code}: {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise Exception(f"Upload failed: {response.text}")
                        
            except Exception as e:
                logger.error(f"HTTP Upload attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise e
        
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