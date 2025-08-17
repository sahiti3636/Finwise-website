# 🚀 Finwise Deployment Guide - Managed Services Path

This guide will walk you through deploying your Finwise project using managed services:
- **Backend**: Django on Render
- **Database**: PostgreSQL on Neon
- **Frontend**: React on Vercel

## 📋 Prerequisites

- GitHub repository with your Finwise project
- Neon account (free tier available)
- Render account (free tier available)
- Vercel account (free tier available)
- Gemini AI API key

## 🗄️ Step 1: Create PostgreSQL Database (Neon)

1. **Sign up/Login to Neon**
   - Go to [neon.tech](https://neon.tech)
   - Create account or login

2. **Create New Project**
   - Click "New Project"
   - Choose a project name (e.g., "finwise-db")
   - Select a region close to your users
   - Click "Create Project"

3. **Get Connection String**
   - After project creation, you'll see a connection string
   - Copy the connection string (looks like: `postgresql://user:password@host/database`)
   - **Save this for Step 2**

## ⚙️ Step 2: Deploy Django Backend (Render)

1. **Sign up/Login to Render**
   - Go to [render.com](https://render.com)
   - Create account or login

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select your Finwise repository

3. **Configure Service**
   - **Name**: `finwise-api` (or your preferred name)
   - **Root Directory**: `finwise_backend`
   - **Runtime**: Python 3
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**: 
     ```bash
     gunicorn finwise_backend.wsgi_production:application --bind 0.0.0.0:8000
     ```

4. **Set Environment Variables**
   ```
   DEBUG=False
   SECRET_KEY=<generate-strong-random-key>
   DATABASE_URL=<your-neon-connection-string>
   GEMINI_API_KEY=<your-gemini-api-key>
   ALLOWED_HOSTS=<your-render-service.onrender.com>
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

5. **Create Web Service**
   - Click "Create Web Service"
   - Wait for first deployment (5-10 minutes)
   - Note your API URL (e.g., `https://finwise-api.onrender.com`)

6. **Create Admin User**
   - Once deployed, go to your service dashboard
   - Click "Shell" tab
   - Run: `python manage.py createsuperuser`
   - Follow prompts to create admin account

## 🌐 Step 3: Deploy React Frontend (Vercel)

1. **Sign up/Login to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Create account or login

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import from GitHub
   - Select your Finwise repository

3. **Configure Project**
   - **Framework Preset**: Vite
   - **Root Directory**: `project_frontend/projectv2_v`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. **Set Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add: `VITE_API_BASE_URL=https://your-render-service.onrender.com/api`
   - Replace with your actual Render API URL

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment (2-3 minutes)
   - Note your frontend URL (e.g., `https://finwise-website.vercel.app`)

## 🔒 Step 4: Security & CORS Configuration

1. **Update Backend CORS**
   - In Render dashboard, go to Environment Variables
   - Update `CORS_ALLOWED_ORIGINS` with your Vercel URL:
     ```
     https://your-frontend.vercel.app
     ```

2. **Update ALLOWED_HOSTS**
   - Ensure `ALLOWED_HOSTS` includes your Render domain:
     ```
     your-render-service.onrender.com
     ```

3. **Redeploy Backend**
   - Render will automatically redeploy when you change environment variables

## 🌍 Step 5: Custom Domain (Optional)

### Frontend Domain
1. In Vercel dashboard, go to Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Vercel will provision SSL automatically

### Backend Domain
1. In Render dashboard, go to Settings → Domains
2. Add your custom domain
3. Update DNS records
4. Render will provision SSL automatically

## ✅ Production Checklist

- [ ] `DEBUG=False` in backend
- [ ] Strong `SECRET_KEY` generated
- [ ] Database connected to PostgreSQL (Neon)
- [ ] Static files collected
- [ ] Admin user created
- [ ] CORS properly configured
- [ ] Frontend API URL correctly set
- [ ] SSL certificates working
- [ ] All environment variables set

## 🔧 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check requirements.txt has all dependencies
   - Verify Python version compatibility
   - Check build logs in Render dashboard

2. **Database Connection Issues**
   - Verify DATABASE_URL format
   - Check Neon database is running
   - Ensure IP allowlist includes Render

3. **CORS Errors**
   - Verify CORS_ALLOWED_ORIGINS includes frontend URL
   - Check frontend is using correct API URL
   - Ensure backend is redeployed after CORS changes

4. **Static Files Not Loading**
   - Verify STATIC_ROOT is set correctly
   - Check collectstatic command in build
   - Ensure whitenoise middleware is added

### Useful Commands

```bash
# Check backend logs
# In Render dashboard → Logs tab

# Check frontend build
# In Vercel dashboard → Deployments → View logs

# Test API endpoints
curl https://your-api.onrender.com/api/health/

# Test frontend
# Open your Vercel URL in browser
```

## 📊 Monitoring & Maintenance

1. **Render Dashboard**
   - Monitor service health
   - Check logs for errors
   - Monitor resource usage

2. **Vercel Dashboard**
   - Monitor deployment status
   - Check analytics
   - Monitor performance

3. **Neon Dashboard**
   - Monitor database performance
   - Check connection usage
   - Monitor storage usage

## 🎉 Success!

Your Finwise project is now deployed and accessible worldwide! 

- **Frontend**: `https://your-frontend.vercel.app`
- **Backend API**: `https://your-api.onrender.com`
- **Database**: Neon PostgreSQL (managed)

The system will automatically scale and handle traffic, with SSL certificates and CDN distribution included. 