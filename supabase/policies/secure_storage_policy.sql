-- Secure Storage Policy for OPG Images
-- This script locks down the storage bucket to ensure privacy for medical data.
-- It requires the backend to use the SERVICE_KEY for operations.

-- 1. Make the bucket PRIVATE (disable public URLs)
update storage.buckets 
set public = false 
where id = 'opg-images';

-- 2. Revoke Public Policies (Drop existing permissive policies)

-- Drop Upload Policy
drop policy if exists "Allow Public Uploads" on storage.objects;

-- Drop Select Policy (Viewing)
-- With a private bucket, public URLs will stop working. 
-- The application must use Signed URLs (which it does).
drop policy if exists "Allow Public Select" on storage.objects;

-- Drop Delete Policy
drop policy if exists "Allow Public Delete" on storage.objects;

-- 3. (Optional) Explicitly deny anon access if needed, but dropping allowable policies 
-- on a private bucket is usually sufficient as the default is DENY.

-- NOTE: After running this, ensure your .env has SUPABASE_SERVICE_KEY set currently
-- or uploads will fail!
