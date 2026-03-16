# Debugging OPG Upload Internal Server Error

## Step 1: Check Vercel Logs

Since you're still getting an Internal Server Error, we need to check the Vercel logs to see the detailed error messages we added.

### Access Vercel Logs:

1. **Via Vercel Dashboard:**
   - Go to https://vercel.com/dashboard
   - Select your project
   - Click on "Deployments"
   - Click on the latest deployment (should be the one with commit "Fix OPG upload")
   - Click on "Functions" or "Runtime Logs"
   - Try uploading an OPG image again
   - Watch the logs in real-time

2. **Look for these specific log messages:**
   ```
   Processing OPG upload for patient [id], file: [filename]
   Secured filename: [filename]
   Imported Supabase storage utilities
   Starting upload to Supabase for file: [filename]
   ```

3. **Common error patterns to look for:**

   **Error 1: Missing Environment Variables**
   ```
   Supabase configuration error: SUPABASE_URL and SUPABASE_KEY must be set
   ```
   **Solution:** Add SUPABASE_URL and SUPABASE_KEY to Vercel environment variables

   **Error 2: Bucket doesn't exist**
   ```
   Upload to Supabase failed: Bucket not found
   ```
   **Solution:** Create the `opg-images` bucket in Supabase Storage

   **Error 3: Permission denied**
   ```
   Upload to Supabase failed: new row violates row-level security policy
   ```
   **Solution:** Update Supabase Storage policies (see below)

## Step 2: Verify Vercel Environment Variables

Go to Vercel Dashboard → Your Project → Settings → Environment Variables

**Required variables:**
- `SUPABASE_URL` = `https://cvctulmujgdnzozhpwmk.supabase.co`
- `SUPABASE_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN2Y3R1bG11amdkbnpvemhwd21rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4ODIyNjcsImV4cCI6MjA4NDQ1ODI2N30.SxZ7eDnSY99ZQBgWmRfk2xHvxalJHCrqyzYlsJ_pNyc`
- `SUPABASE_DB_URL` = `postgresql://postgres.cvctulmujgdnzozhpwmk:UDMMisthebest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres`

**IMPORTANT:** After adding/updating environment variables, you MUST redeploy:
- Go to Deployments → Latest deployment → Click "..." → Redeploy

## Step 3: Verify Supabase Storage Configuration

### Check if bucket exists:
1. Go to https://supabase.com/dashboard
2. Select your project: `cvctulmujgdnzozhpwmk`
3. Click "Storage" in the left sidebar
4. Look for a bucket named `opg-images`

### If bucket doesn't exist, create it:
1. Click "Create a new bucket"
2. Name: `opg-images`
3. Public bucket: **No** (we'll use signed URLs)
4. Click "Create bucket"

### Configure Storage Policies:

1. Click on the `opg-images` bucket
2. Click "Policies" tab
3. Click "New Policy"

**Policy 1: Allow authenticated uploads**
```sql
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'opg-images');
```

**Policy 2: Allow public reads (for viewing images)**
```sql
CREATE POLICY "Allow public reads"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'opg-images');
```

**Policy 3: Allow authenticated deletes (for replacing images)**
```sql
CREATE POLICY "Allow authenticated deletes"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'opg-images');
```

## Step 4: Test with Enhanced Logging

After verifying the above:

1. **Redeploy on Vercel** (if you changed environment variables)
2. **Open Vercel Runtime Logs** in a separate tab
3. **Try uploading an OPG image** from supervisor dashboard
4. **Watch the logs** - you should see detailed messages at each step

## Step 5: Alternative - Check Application Logs

If you can't access Vercel logs easily, let's add a temporary debugging endpoint:

Add this to your `app.py` (after the health check endpoint):

```python
@app.route('/debug/storage-config')
def debug_storage_config():
    """Debug endpoint to check Supabase storage configuration"""
    import os
    return {
        'supabase_url': os.environ.get('SUPABASE_URL', 'NOT SET'),
        'supabase_key_set': bool(os.environ.get('SUPABASE_KEY')),
        'supabase_db_url_set': bool(os.environ.get('SUPABASE_DB_URL'))
    }
```

Then visit: `https://your-app.vercel.app/debug/storage-config`

## Step 6: Common Issues and Solutions

### Issue: "Module not found: supabase"
**Solution:** Ensure `supabase` is in `requirements.txt`
```bash
# Check requirements.txt contains:
supabase>=2.0.0
```

### Issue: "Cannot import name 'create_client'"
**Solution:** Update supabase package version in requirements.txt

### Issue: Upload succeeds but returns None
**Solution:** This is what our fix addresses - check the signed URL generation logs

## Quick Test Script

If you want to test locally first, create a test file:

```python
# test_upload.py
import os
from dotenv import load_dotenv
from utils.storage import get_supabase_client

load_dotenv()

try:
    client = get_supabase_client()
    print("✅ Supabase client created successfully")
    
    # Test bucket access
    buckets = client.storage.list_buckets()
    print(f"✅ Available buckets: {[b.name for b in buckets]}")
    
    # Check if opg-images exists
    if any(b.name == 'opg-images' for b in buckets):
        print("✅ opg-images bucket exists")
    else:
        print("❌ opg-images bucket NOT FOUND - create it in Supabase dashboard")
        
except Exception as e:
    print(f"❌ Error: {e}")
```

Run: `python test_upload.py`

## Next Steps

1. Check Vercel logs first - this will tell you exactly what's failing
2. Verify environment variables are set in Vercel
3. Verify Supabase bucket and policies exist
4. Share the error message from Vercel logs if still failing

The enhanced logging we added will show you exactly where the upload is failing!
