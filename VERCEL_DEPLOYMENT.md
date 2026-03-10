# 🚀 Vercel Deployment Guide

Complete guide to deploy your Dental Blinding Process Project to Vercel.

---

## 📋 Prerequisites

Before deploying to Vercel, ensure you have:

1. ✅ Supabase database configured and running
2. ✅ Supabase Storage bucket `opg-images` created
3. ✅ All environment variables ready (from `.env` file)
4. ✅ Vercel account (free tier works fine)
5. ✅ Git repository (GitHub, GitLab, or Bitbucket)

---

## 🔧 Step 1: Prepare Your Project

### 1.1 Verify Vercel Configuration Files

Your project now has these Vercel-specific files:

- ✅ **`vercel.json`** - Vercel configuration
- ✅ **`index.py`** - Vercel entry point
- ✅ **`requirements.txt`** - Python dependencies

### 1.2 Create `.vercelignore` File

Create a `.vercelignore` file to exclude unnecessary files:

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.log
.env
.venv
venv/
uploads/
.DS_Store
.idea/
.vscode/
*.swp
*.swo
auth.log
```

### 1.3 Update `.gitignore`

Ensure your `.gitignore` includes:

```
.env
.vercel
uploads/
*.log
__pycache__/
```

---

## 📦 Step 2: Push to Git Repository

### 2.1 Initialize Git (if not already done)

```bash
cd /Users/sittminthar/Downloads/Dental-Blinding-Process-Project-master
git init
git add .
git commit -m "Initial commit - Supabase migration complete"
```

### 2.2 Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Create a new repository (e.g., `dental-blinding-process`)
3. **Do NOT** initialize with README (your project already has files)

### 2.3 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/dental-blinding-process.git
git branch -M main
git push -u origin main
```

---

## 🌐 Step 3: Deploy to Vercel

### 3.1 Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

### 3.2 Deploy via Vercel Dashboard (Recommended)

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**

2. **Click "Add New Project"**

3. **Import Git Repository**
   - Select your GitHub repository
   - Click "Import"

4. **Configure Project**
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty

5. **Add Environment Variables**
   
   Click "Environment Variables" and add the following:

   | Name | Value |
   |------|-------|
   | `SUPABASE_URL` | `https://cvctulmujgdnzozhpwmk.supabase.co` |
   | `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (your anon key) |
   | `SUPABASE_DB_URL` | `postgresql://postgres.cvctulmujgdnzozhpwmk:UDMMisthebest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres` |
   | `SECRET_KEY` | `dental-blinding-process-secret-key-2026` (or generate a new one) |
   | `SUPERVISOR_PASSWORD` | `Dental@2026` |
   | `PI_PASSWORD` | `Dental@2026` |
   | `FLASK_ENV` | `production` |

   > **Important**: For all variables, select **Production**, **Preview**, and **Development** environments.

6. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete (2-3 minutes)

### 3.3 Deploy via Vercel CLI (Alternative)

```bash
# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name? dental-blinding-process
# - Directory? ./
# - Override settings? No

# Add environment variables
vercel env add SUPABASE_URL
vercel env add SUPABASE_KEY
vercel env add SUPABASE_DB_URL
vercel env add SECRET_KEY
vercel env add SUPERVISOR_PASSWORD
vercel env add PI_PASSWORD
vercel env add FLASK_ENV

# Deploy to production
vercel --prod
```

---

## 🗄️ Step 4: Initialize Database on Vercel

After deployment, you need to initialize the database:

### Option 1: Run Setup Script Locally

Since the database is on Supabase, you can initialize it from your local machine:

```bash
python setup_db.py
```

This will create tables and default users in your Supabase database.

### Option 2: Create a Setup Endpoint (Temporary)

Add a temporary setup endpoint to initialize the database remotely. This is already available at `/setup` in your app.

1. Visit: `https://your-app.vercel.app/setup`
2. This will initialize the database
3. You should see: "Database initialized successfully!"

> **Security Note**: After initialization, you may want to disable this endpoint in production by setting an environment variable check.

---

## 🔍 Step 5: Verify Deployment

### 5.1 Check Deployment Status

1. Go to your Vercel dashboard
2. Click on your project
3. Check the "Deployments" tab
4. Ensure status is "Ready"

### 5.2 Test the Application

1. **Visit your app**: `https://your-app.vercel.app`
2. **Login with supervisor account**:
   - Username: `supervisor`
   - Password: `Dental@2026`
3. **Test key features**:
   - Create a patient
   - Upload an OPG image
   - Assign codes
   - View blinded data

### 5.3 Check Logs

If you encounter issues:

1. Go to Vercel dashboard
2. Click on your project
3. Click on the deployment
4. Click "View Function Logs"
5. Check for errors

---

## 🎯 Step 6: Configure Custom Domain (Optional)

### 6.1 Add Custom Domain

1. Go to your project in Vercel dashboard
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

### 6.2 Update DNS Records

Add the following DNS records at your domain registrar:

- **Type**: CNAME
- **Name**: www (or @)
- **Value**: cname.vercel-dns.com

---

## 🔒 Step 7: Security Considerations

### 7.1 Secure Environment Variables

- ✅ Never commit `.env` to Git
- ✅ Use strong passwords for production
- ✅ Rotate `SECRET_KEY` regularly
- ✅ Use Vercel's environment variable encryption

### 7.2 Update Passwords

After deployment, change default passwords:

1. Login as supervisor
2. Go to user management
3. Update passwords for both accounts

### 7.3 Enable HTTPS

Vercel automatically provides HTTPS for all deployments. Ensure your app redirects HTTP to HTTPS (already configured in `app.py`).

---

## 🐛 Troubleshooting

### Issue: "Application Error"

**Solution**: Check Vercel function logs for errors. Common issues:
- Missing environment variables
- Database connection timeout
- Import errors

### Issue: "Database connection failed"

**Solution**: 
1. Verify `SUPABASE_DB_URL` is correct
2. Check Supabase dashboard for database status
3. Ensure IP is not blocked in Supabase settings

### Issue: "Static files not loading"

**Solution**:
1. Check `vercel.json` routes configuration
2. Ensure static files are in `static/` directory
3. Clear browser cache

### Issue: "Image upload fails"

**Solution**:
1. Verify `SUPABASE_URL` and `SUPABASE_KEY` are set
2. Check Supabase Storage bucket `opg-images` exists
3. Verify bucket permissions in Supabase dashboard

### Issue: "Function timeout"

**Solution**:
- Vercel free tier has 10-second timeout
- Optimize database queries
- Consider upgrading to Pro plan for 60-second timeout

---

## 📊 Monitoring and Maintenance

### Monitor Application

1. **Vercel Analytics**: Enable in project settings
2. **Function Logs**: Check regularly for errors
3. **Supabase Dashboard**: Monitor database usage

### Regular Maintenance

- Update dependencies: `pip list --outdated`
- Check Vercel deployment logs weekly
- Monitor Supabase storage usage
- Backup database regularly

---

## 🎉 Deployment Checklist

- [ ] Git repository created and pushed
- [ ] Vercel project created
- [ ] All environment variables added
- [ ] Database initialized via `/setup` endpoint
- [ ] Login tested with supervisor account
- [ ] Patient creation tested
- [ ] Image upload tested
- [ ] Blinded data generation tested
- [ ] Custom domain configured (optional)
- [ ] Default passwords changed

---

## 📞 Support Resources

- **Vercel Documentation**: https://vercel.com/docs
- **Supabase Documentation**: https://supabase.com/docs
- **Flask Documentation**: https://flask.palletsprojects.com/

---

## 🚀 Quick Deploy Commands

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/dental-blinding-process.git
cd dental-blinding-process

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod

# Initialize database (run locally)
python setup_db.py
```

---

**Your app is now live on Vercel! 🎊**

Access it at: `https://your-project-name.vercel.app`
