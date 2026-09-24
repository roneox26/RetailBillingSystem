# Render Deployment সমাধান

## সমস্যা কী ছিল?
Gunicorn `app.py` module খুঁজে পাচ্ছিল না কারণ project structure সঠিক ছিল না।

## কী ঠিক করা হয়েছে?

### 1. **Gunicorn Configuration** (`gunicorn.conf.py`)
- সঠিক port binding (Render এর $PORT environment variable)
- Workers এবং threads configuration
- Logging setup

### 2. **Procfile আপডেট**
```
web: gunicorn --chdir RetailBillingSystem --config RetailBillingSystem/gunicorn.conf.py wsgi:app
```

### 3. **render.yaml আপডেট**
- সঠিক startCommand
- PORT environment variable যোগ করা

### 4. **.renderignore ফাইল**
- অপ্রয়োজনীয় ফাইল deploy থেকে বাদ দেওয়া

## Render এ Deploy করার ধাপ

### Step 1: GitHub এ Push করুন
```bash
git add .
git commit -m "Fixed Render deployment configuration"
git push origin main
```

### Step 2: Render Dashboard এ যান
1. https://dashboard.render.com এ লগইন করুন
2. "New +" বাটনে ক্লিক করুন
3. "Web Service" সিলেক্ট করুন

### Step 3: Repository Connect করুন
1. আপনার GitHub repository সিলেক্ট করুন
2. Branch: `main` সিলেক্ট করুন

### Step 4: Configuration (যদি render.yaml না থাকে)
- **Name**: retail-billing-system
- **Environment**: Python
- **Build Command**: `bash build.sh`
- **Start Command**: `gunicorn --chdir RetailBillingSystem --config RetailBillingSystem/gunicorn.conf.py wsgi:app`

### Step 5: Environment Variables সেট করুন
Render Dashboard এ Environment Variables যোগ করুন:
- `SESSION_SECRET`: একটি random secret key (Auto-generate করতে পারেন)
- `FLASK_ENV`: `production`
- `PORT`: `10000` (Render automatically সেট করবে)

### Step 6: Deploy করুন
"Create Web Service" বাটনে ক্লিক করুন।

## Deployment চেক করুন

Deploy হওয়ার পর logs দেখুন:
- ✅ "Database tables created" দেখা উচিত
- ✅ "Booting worker" দেখা উচিত
- ✅ "Listening at: http://0.0.0.0:10000" দেখা উচিত

## সাধারণ সমস্যা ও সমাধান

### 1. ModuleNotFoundError: No module named 'app'
**সমাধান**: `--chdir RetailBillingSystem` ব্যবহার করুন gunicorn command এ

### 2. Port scan timeout
**সমাধান**: নিশ্চিত করুন gunicorn `0.0.0.0:$PORT` এ bind করছে

### 3. Database error
**সমাধান**: `build.sh` এ `python setup_db.py` চালু আছে কিনা চেক করুন

### 4. Import errors
**সমাধান**: `requirements.txt` এ সব dependencies আছে কিনা চেক করুন

## Local এ Test করুন

Deploy করার আগে local এ test করুন:

```bash
cd RetailBillingSystem
gunicorn --config gunicorn.conf.py wsgi:app
```

Browser এ খুলুন: http://localhost:10000

## Production Database (Optional)

Free tier এ SQLite ব্যবহার হচ্ছে। Production এর জন্য PostgreSQL ব্যবহার করতে চাইলে:

1. Render এ PostgreSQL database তৈরি করুন
2. `DATABASE_URL` environment variable সেট করুন
3. `requirements.txt` এ `psycopg2-binary` যোগ করুন

## সাহায্য দরকার?

- Render Docs: https://render.com/docs
- Logs দেখুন: Render Dashboard > Your Service > Logs
- GitHub Issues: আপনার repository তে issue তৈরি করুন

---

**সফল Deployment এর জন্য শুভকামনা! 🚀**
