# 🚀 Deployment Guide - Retail Billing System

## ✅ Production Ready Features

- ✓ User Authentication (Signup/Login)
- ✓ Session Management
- ✓ Password Hashing
- ✓ Input Validation
- ✓ Error Handling
- ✓ Caching
- ✓ Pagination
- ✓ Discount & VAT
- ✓ Multi-user Support
- ✓ Organization Isolation

## 📦 Deployment Options

### Option 1: Heroku

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SESSION_SECRET=your-secret-key-here
heroku config:set FLASK_ENV=production

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku main

# Run database setup
heroku run python RetailBillingSystem/setup_db.py
```

### Option 2: Railway

1. Go to https://railway.app
2. Connect GitHub repository
3. Add environment variables:
   - `SESSION_SECRET`: your-secret-key
   - `FLASK_ENV`: production
4. Deploy automatically

### Option 3: Render

1. Go to https://render.com
2. Create new Web Service
3. Connect repository
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `cd RetailBillingSystem && gunicorn wsgi:app`
6. Add environment variables

### Option 4: PythonAnywhere

1. Upload files to PythonAnywhere
2. Create virtual environment
3. Install requirements
4. Configure WSGI file
5. Reload web app

### Option 5: VPS (DigitalOcean, AWS, etc.)

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Clone repository
git clone your-repo-url
cd RetailBillingSystem

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Setup database
cd RetailBillingSystem
python setup_db.py

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 wsgi:app

# Configure Nginx (reverse proxy)
# Setup systemd service for auto-start
```

## 🔧 Environment Variables

Create `.env` file:

```env
SESSION_SECRET=your-very-secret-key-change-this
FLASK_ENV=production
DATABASE_URL=sqlite:///retail_billing.db
```

**Important:** Change `SESSION_SECRET` to a random string!

Generate secret key:
```python
import secrets
print(secrets.token_hex(32))
```

## 🗄️ Database Setup

After deployment, run:

```bash
python RetailBillingSystem/setup_db.py
```

This creates:
- Demo user: `admin@demo.com` / `admin123`
- Sample products

## 🔒 Security Checklist

- ✅ Change SESSION_SECRET
- ✅ Set FLASK_ENV=production
- ✅ Use HTTPS (SSL certificate)
- ✅ Change demo user password
- ✅ Regular backups
- ✅ Update dependencies

## 📊 Production Configuration

Update `config.py` for production:

```python
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Use PostgreSQL for production
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

## 🚀 Quick Deploy Commands

### Local Testing (Production Mode)

```bash
export FLASK_ENV=production
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

### With Workers

```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:app
```

## 📝 Post-Deployment

1. Test all features
2. Change demo password
3. Create your organization
4. Add products
5. Test billing & reports
6. Setup backups

## 🔄 Updates

To update deployed app:

```bash
git pull origin main
pip install -r requirements.txt
# Restart application
```

## 📞 Support

For issues:
1. Check logs
2. Verify environment variables
3. Test database connection
4. Check file permissions

## 🎉 Your App is Ready!

Access your deployed app and login with:
- Email: `admin@demo.com`
- Password: `admin123`

**Remember to change the password immediately!**

---

Built with ❤️ using Flask
Enhanced by Amazon Q Developer
