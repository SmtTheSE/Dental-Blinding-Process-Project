-- Create the bucket if it doesn't exist
insert into storage.buckets (id, name, public) 
values ('opg-images', 'opg-images', true)
on conflict (id) do nothing;

-- Policies for "opg-images" bucket
-- We use 'drop policy if exists' to ensure we can re-run this script without errors

-- 1. Allow Public Uploads
drop policy if exists "Allow Public Uploads" on storage.objects;
create policy "Allow Public Uploads"
on storage.objects for insert
with check ( bucket_id = 'opg-images' );

-- 2. Allow Public Select (Viewing)
drop policy if exists "Allow Public Select" on storage.objects;
create policy "Allow Public Select"
on storage.objects for select
using ( bucket_id = 'opg-images' );

-- 3. Allow Public Delete
drop policy if exists "Allow Public Delete" on storage.objects;
create policy "Allow Public Delete"
on storage.objects for delete
using ( bucket_id = 'opg-images' );
