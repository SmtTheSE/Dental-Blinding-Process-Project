# 🖼️ Fix UDMM Logo on Vercel

## Issue
The UDMM logo (`/static/img/UDMM.jpeg`) is not appearing on Vercel deployment.

## Solution Applied

### 1. Updated `vercel.json`

Added static file build configuration to ensure images are properly served:

```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    },
    {
      "src": "static/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### 2. Verify Logo File Exists

Confirmed that the logo file exists at:
- **Path**: `/static/img/UDMM.jpeg`
- **Size**: 17,218 bytes
- **Used in**: 
  - Header navigation (line 618 in `base.html`)
  - Footer (line 676 in `base.html`)

### 3. Deploy Changes

After updating `vercel.json`, you need to redeploy:

```bash
# Commit changes
git add vercel.json
git commit -m "Fix static file serving for UDMM logo"
git push

# Vercel will automatically redeploy
```

### 4. Verify After Deployment

1. Visit your Vercel app
2. Check browser console (F12) for any 404 errors
3. Verify logo appears in:
   - Header (top navigation)
   - Footer (bottom of page)

## Alternative Solutions

### If Logo Still Doesn't Appear

**Option 1: Check File Case Sensitivity**

Vercel is case-sensitive. Ensure the file is named exactly:
- `UDMM.jpeg` (not `udmm.jpeg` or `UDMM.JPEG`)

**Option 2: Convert to Base64 (Embedded)**

If static file serving continues to fail, embed the logo as base64:

```bash
# Convert image to base64
base64 static/img/UDMM.jpeg > udmm_base64.txt
```

Then update `base.html`:

```html
<!-- Replace this -->
<img src="/static/img/UDMM.jpeg" alt="UDMM Logo" class="logo">

<!-- With this -->
<img src="data:image/jpeg;base64,/9j/4AAQSkZJRg..." alt="UDMM Logo" class="logo">
```

**Option 3: Use Supabase Storage**

Upload logo to Supabase Storage and use the URL:

```python
# Upload to Supabase Storage
from utils.storage import upload_image

# Then update base.html with Supabase URL
<img src="https://cvctulmujgdnzozhpwmk.supabase.co/storage/v1/object/public/opg-images/UDMM.jpeg" alt="UDMM Logo" class="logo">
```

## Recommended Approach

1. ✅ **First**: Try the updated `vercel.json` (already done)
2. ✅ **Redeploy**: Push changes to trigger Vercel rebuild
3. ✅ **Test**: Check if logo appears after deployment
4. ⚠️ **If fails**: Use Option 3 (Supabase Storage) for reliability

## Testing Checklist

After redeployment:

- [ ] Logo appears in header navigation
- [ ] Logo appears in footer
- [ ] No 404 errors in browser console
- [ ] Logo loads on mobile view
- [ ] Logo loads on desktop view

---

**Status**: Configuration updated. Redeploy to apply changes.
