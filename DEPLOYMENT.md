# 🦷 Dental Age Estimation System — Free Production Deployment Guide

This guide explains how to deploy the Dental Age Estimation System on Render (free tier) while using Supabase (free tier) for safe OPG image storage.
This ensures the project is completely free while keeping images and data secure.

## ✅ Prerequisites

- A Render.com account (free)
- A Supabase.com account (free)
- GitHub repository with your project code

## ⚙️ Deployment Steps

### 1. Fork or Clone the Repository

Make sure your code is in a GitHub repository accessible by Render.

### 2. Set Up Supabase (for OPG Image Storage)

1. Go to [Supabase](https://supabase.com/) → sign up (free plan).
2. Create a new project (choose free database size).
3. Navigate to Storage → create a bucket named `opg-images`.
4. Make it private (recommended for patient data).
5. Go to Project Settings → API and note down:
   - PROJECT_URL
   - ANON_KEY
   - SERVICE_ROLE_KEY (optional for admin ops)

### 3. Set Up Render Web Service

1. Log in to Render → click New → Web Service
2. Connect your GitHub repo
3. Configure service:
   - Name: `dental-age-estimation`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`
   - Plan: Free

### 4. Add Environment Variables

In Render dashboard → your web service → Environment Variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `FLASK_ENV` | production | Yes |
| `SECRET_KEY` | Strong random string (≥32 chars) | Yes |
| `DATABASE_URL` | Auto-provided by Render | Yes |
| `SUPABASE_URL` | From Supabase → Project Settings → API | Yes |
| `SUPABASE_KEY` | Supabase anon key (for uploads) | Yes |

### 5. Deploy

Click Create Web Service → Render will build and deploy.

## 🚀 Post-Deployment Setup

### 1. Initialize Database

Visit: `https://your-app.onrender.com/setup`

This creates tables + default accounts.

### 2. Default Accounts

- Supervisor: `supervisor` / (password from logs or env var)
- PI: `pi` / (password from logs or env var)

⚠️ Change passwords immediately.

## 📂 OPG Image Storage (Supabase Integration)

The application now stores OPG images in Supabase storage rather than local filesystem storage. This ensures that images persist even when the Render service restarts.

### Implementation Details

In your Flask app, OPG images are automatically uploaded to Supabase storage using the following code:

```python
# utils/storage.py
import os
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_image(file, filename):
    """Upload OPG image to Supabase storage and return public URL."""
    bucket = "opg-images"
    # Upload binary data
    res = supabase.storage.from_(bucket).upload(filename, file.read())
    if res.get("error"):
        raise Exception(res["error"]["message"])
    # Generate public URL
    return supabase.storage.from_(bucket).get_public_url(filename)
```

### Usage in Flask Route

```python
from utils.storage import upload_image

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    filename = secure_filename(file.filename)
    url = upload_image(file, filename)
    # Store URL + patient metadata in PostgreSQL
    save_to_db(filename, url, patient_data)
    return {"status": "success", "url": url}
```

## 🔒 Security Considerations

1. Keep `SUPABASE_KEY` secret (do not expose in frontend).
2. Make Supabase bucket private if storing sensitive patient data.
3. Use signed URLs (Supabase supports time-limited download links).
4. Always use HTTPS in production (Render provides this automatically).

## 📈 Scaling (Free Plan Constraints)

- Render Free: 512 MB RAM, 1 GB DB → fine for small traffic.
- Supabase Free: 5 GB storage → thousands of OPG images.
- If dataset grows > 5 GB → move to paid Supabase storage (~$5/mo).

## 🛠️ Troubleshooting

- App won't start → Check logs in Render dashboard.
- File upload fails → Check Supabase bucket permissions.
- DB full → Backup + clean old data.

## 🔄 Updating the Application

1. Push code changes to GitHub → Render auto-deploys.
2. Storage code changes require no Supabase redeploy.

## 💾 Backup & Recovery

- Database: use `pg_dump` → save SQL backups to Supabase storage.
- Images: already safe in Supabase.

## 🎯 Final Outcome

- Web app hosted on Render Free Tier
- PostgreSQL DB hosted on Render Free Tier
- OPG images permanently stored on Supabase Free Tier (5 GB)
- Zero cost production-ready deployment