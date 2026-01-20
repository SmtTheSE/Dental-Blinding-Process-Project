# Supabase Migration - Quick Reference

## 🎯 What Changed

Your Dental Blinding Process Project now uses **Supabase** instead of Render for:
- PostgreSQL database (via Transaction Pooler)
- Image storage (already implemented)

## 🔑 Default Login Credentials

| Username   | Password     | Role                  |
|------------|--------------|----------------------|
| supervisor | Dental@2026  | Supervisor           |
| pi         | Dental@2026  | Principal Investigator |

## 🧪 Testing Commands

### Test Database Connection
```bash
python test_supabase_connection.py
```

### Test CRUD Operations
```bash
python test_supabase_crud.py
```

### Initialize Database
```bash
python setup_db.py
```

### Run Application
```bash
python run.py
```

## 📁 Important Files

- **`.env`** - Your Supabase credentials (not committed to git)
- **`.env.example`** - Template for environment variables
- **`config.py`** - Database configuration
- **`setup_db.py`** - Database initialization script
- **`test_supabase_connection.py`** - Connection test script
- **`test_supabase_crud.py`** - CRUD operations test script

## 🔧 Environment Variables

```env
SUPABASE_URL=https://cvctulmujgdnzozhpwmk.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_DB_URL=postgresql://postgres.cvctulmujgdnzozhpwmk:PASSWORD@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
SECRET_KEY=your-secret-key
SUPERVISOR_PASSWORD=Dental@2026
PI_PASSWORD=Dental@2026
```

## ✅ Verification Checklist

- [x] Database connection successful
- [x] Tables created (user, patient, estimation_entry)
- [x] Default users created
- [x] CRUD operations working
- [x] Image storage configured

## 🚀 Next Steps

1. **Test locally**: Run `python run.py` and access `http://localhost:5001`
2. **Login**: Use supervisor or pi account
3. **Test features**: Upload images, create patients, generate blinded data
4. **Deploy**: Set environment variables on your hosting platform

## 📊 Database Info

- **PostgreSQL Version**: 17.6
- **Connection**: Transaction Pooler (port 6543)
- **Tables**: 3 (user, patient, estimation_entry)
- **Users**: 2 (supervisor, pi)
- **Patients**: 0 (ready for data)

## 🔒 Security Notes

- `.env` file is in `.gitignore` (not committed)
- Passwords are hashed using Werkzeug
- SSL mode required for database connections
- Signed URLs for image access (1-year expiry)

---

**Everything is ready to use! The project flow remains exactly the same.**
