# 🚀 Deployment Guide

This guide covers deploying the Expense Management System to production.

---

## 📋 Pre-Deployment Checklist

- [ ] All features tested and working locally
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Production Supabase project created
- [ ] Storage bucket configured
- [ ] SSL certificates ready (automatic with most platforms)

---

## 🗄️ Database Setup (Supabase)

### 1. Create Production Project
1. Go to [supabase.com](https://supabase.com)
2. Create a new project (choose nearest region)
3. Wait for project initialization (~2 minutes)

### 2. Run Migrations
1. Go to SQL Editor in Supabase Dashboard
2. Run migrations in order:
   ```sql
   -- 1. Add approval rule columns
   -- Copy from: backend/migrations/add_approval_rule_columns.sql
   
   -- 2. Fix approval rule approvers
   -- Copy from: backend/migrations/fix_approval_rule_approvers.sql
   ```

### 3. Configure Storage
1. Go to Storage > Create bucket
2. Bucket name: `receipts`
3. Public bucket: ✅ Yes
4. File size limit: 5MB
5. Allowed MIME types: `image/*`

### 4. Set Up RLS (Row Level Security)
```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE approvals ENABLE ROW LEVEL SECURITY;

-- Add policies as needed
```

---

## 🔧 Backend Deployment

### Option 1: Railway

1. **Install Railway CLI**
   ```bash
   npm install -g railway
   ```

2. **Login and Initialize**
   ```bash
   railway login
   cd backend
   railway init
   ```

3. **Add Environment Variables**
   ```bash
   railway variables set SUPABASE_URL=your_url
   railway variables set SUPABASE_KEY=your_key
   railway variables set SECRET_KEY=your_secret
   ```

4. **Deploy**
   ```bash
   railway up
   ```

### Option 2: Heroku

1. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set SUPABASE_URL=your_url
   heroku config:set SUPABASE_KEY=your_key
   heroku config:set SECRET_KEY=your_secret
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 3: DigitalOcean App Platform

1. Go to DigitalOcean Dashboard
2. Create new App
3. Connect GitHub repository
4. Select `backend` folder
5. Add environment variables
6. Deploy

---

## 🎨 Frontend Deployment

### Option 1: Vercel (Recommended)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

3. **Set Environment Variables**
   - Go to Vercel Dashboard
   - Project Settings > Environment Variables
   - Add: `NEXT_PUBLIC_API_URL=https://your-backend-url.com`

4. **Redeploy**
   ```bash
   vercel --prod
   ```

### Option 2: Netlify

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Build and Deploy**
   ```bash
   cd frontend
   npm run build
   netlify deploy --prod
   ```

3. **Set Environment Variables**
   - Go to Netlify Dashboard
   - Site Settings > Environment Variables
   - Add: `NEXT_PUBLIC_API_URL`

### Option 3: Docker

1. **Create Dockerfile** (frontend)
   ```dockerfile
   FROM node:18-alpine
   
   WORKDIR /app
   COPY package*.json ./
   RUN npm install
   COPY . .
   
   ENV NEXT_PUBLIC_API_URL=https://your-backend-url.com
   
   RUN npm run build
   EXPOSE 3000
   CMD ["npm", "start"]
   ```

2. **Build and Run**
   ```bash
   docker build -t expense-frontend .
   docker run -p 3000:3000 expense-frontend
   ```

---

## 🔒 Security Configuration

### 1. Update CORS Settings
In `backend/app.py`:
```python
CORS(app, resources={
    r"/*": {
        "origins": ["https://your-frontend-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### 2. Use Strong Secret Keys
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Enable HTTPS
- Vercel/Netlify: Automatic
- Railway: Automatic
- Custom server: Use Let's Encrypt

### 4. Set Secure Headers
Add to Flask app:
```python
@app.after_request
def set_secure_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

## 📊 Monitoring & Logging

### Backend Monitoring
```python
# Add to app.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Error Tracking
Consider adding:
- **Sentry** for error tracking
- **LogRocket** for session replay
- **New Relic** for performance monitoring

---

## 🔄 CI/CD Setup

### GitHub Actions Example
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: |
          npm install -g railway
          railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: |
          npm install -g vercel
          cd frontend
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## ✅ Post-Deployment Checklist

- [ ] Test all API endpoints
- [ ] Test authentication flow
- [ ] Test file uploads
- [ ] Test approval workflow
- [ ] Verify email notifications (if enabled)
- [ ] Check error logging
- [ ] Monitor performance
- [ ] Set up backups
- [ ] Document production URLs
- [ ] Update DNS records

---

## 🆘 Troubleshooting

### Common Issues

**CORS Errors:**
- Update CORS origins in `backend/app.py`
- Ensure frontend URL matches exactly (no trailing slash)

**Database Connection Errors:**
- Verify Supabase credentials
- Check if IP is whitelisted (if using IP restrictions)

**File Upload Errors:**
- Verify storage bucket is public
- Check bucket name matches code
- Verify file size limits

**Authentication Errors:**
- Ensure SECRET_KEY is same across deployments
- Check JWT token expiration settings

---

## 📚 Additional Resources

- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Supabase Production Guide](https://supabase.com/docs/guides/platform/going-into-prod)
- [Railway Docs](https://docs.railway.app/)
- [Vercel Docs](https://vercel.com/docs)

---

**Need help?** Open an issue on GitHub or contact the team.
