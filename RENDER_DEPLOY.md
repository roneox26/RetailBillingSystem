# 🚀 Deploy to Render.com - Step by Step

## ✅ Prerequisites
- GitHub account
- Render.com account (free)
- Code pushed to GitHub

## 📝 Deployment Steps

### Step 1: Go to Render Dashboard
1. Visit: https://render.com
2. Sign up or login
3. Click "New +" button
4. Select "Web Service"

### Step 2: Connect Repository
1. Click "Connect GitHub"
2. Select repository: `roneox26/RetailBillingSystem`
3. Click "Connect"

### Step 3: Configure Service

**Basic Settings:**
- **Name**: `retail-billing-system` (or your choice)
- **Region**: Oregon (US West) - Free tier available
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: Python 3

**Build & Deploy:**
- **Build Command**: 
  ```bash
  pip install -r requirements.txt && cd RetailBillingSystem && python setup_db.py
  ```

- **Start Command**: 
  ```bash
  cd RetailBillingSystem && gunicorn wsgi:app
  ```

### Step 4: Environment Variables

Click "Advanced" and add:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.13.1` |
| `SESSION_SECRET` | Generate random string (click "Generate") |
| `FLASK_ENV` | `production` |

**To generate SESSION_SECRET:**
```python
import secrets
print(secrets.token_hex(32))
```

### Step 5: Select Plan
- Choose **Free** plan
- Click "Create Web Service"

### Step 6: Wait for Deployment
- Render will:
  1. Clone your repository
  2. Install dependencies
  3. Run setup_db.py (creates demo user)
  4. Start the application
- Takes 2-5 minutes

### Step 7: Access Your App
- URL will be: `https://retail-billing-system.onrender.com`
- Or your custom name

### Step 8: Login
```
Email: admin@demo.com
Password: admin123
```

**⚠️ Important: Change password immediately!**

## 🔧 Troubleshooting

### Build Failed?
Check logs for:
- Missing dependencies
- Python version mismatch
- Path issues

### App Not Starting?
Verify:
- Start command is correct
- Environment variables are set
- Database was created

### Database Issues?
Render uses ephemeral storage. For production:
1. Use Render PostgreSQL (free tier available)
2. Update DATABASE_URL in environment variables

## 🔄 Updates

To update your deployed app:

```bash
# Make changes locally
git add .
git commit -m "Update message"
git push origin main
```

Render auto-deploys on push!

## 📊 Monitoring

- View logs in Render dashboard
- Check metrics
- Set up alerts

## 💾 Database Persistence

**Free tier limitation:** SQLite data is lost on restart.

**Solution:** Use PostgreSQL (free tier):

1. In Render dashboard, create PostgreSQL database
2. Copy DATABASE_URL
3. Add to environment variables
4. Update config.py:
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

## 🎯 Custom Domain

1. Go to Settings
2. Add custom domain
3. Update DNS records
4. Enable HTTPS

## ✅ Post-Deployment Checklist

- [ ] App is accessible
- [ ] Can login with demo account
- [ ] Change demo password
- [ ] Create your organization
- [ ] Add products
- [ ] Test billing
- [ ] Test reports
- [ ] Check all features

## 🔗 Useful Links

- **Render Docs**: https://render.com/docs
- **Your App**: https://dashboard.render.com
- **Support**: https://render.com/support

## 🎉 Success!

Your Retail Billing System is now live on Render!

**Share your app:**
- URL: `https://your-app.onrender.com`
- Demo: admin@demo.com / admin123

---

**Note:** Free tier sleeps after 15 min of inactivity. First request may take 30-60 seconds to wake up.
