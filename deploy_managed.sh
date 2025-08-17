#!/bin/bash

# 🚀 Finwise Managed Services Deployment Helper Script
# This script helps prepare and deploy your Finwise project

echo "🚀 Finwise Deployment Helper - Managed Services Path"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "finwise_backend/manage.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "✅ Project structure verified"
echo ""

# Generate a strong secret key
echo "🔑 Generating Django Secret Key..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
echo "Generated Secret Key: $SECRET_KEY"
echo ""

# Check if requirements.txt is updated
echo "📦 Checking requirements.txt..."
if grep -q "gunicorn\|psycopg2\|whitenoise" finwise_backend/requirements.txt; then
    echo "✅ Production dependencies found in requirements.txt"
else
    echo "❌ Warning: Production dependencies may be missing"
    echo "   Make sure requirements.txt includes: gunicorn, psycopg2-binary, whitenoise"
fi
echo ""

# Check if production settings exist
if [ -f "finwise_backend/finwise_backend/settings_production.py" ]; then
    echo "✅ Production settings file found"
else
    echo "❌ Error: Production settings file missing"
    echo "   Please ensure settings_production.py exists"
    exit 1
fi

# Check if production WSGI exists
if [ -f "finwise_backend/finwise_backend/wsgi_production.py" ]; then
    echo "✅ Production WSGI file found"
else
    echo "❌ Error: Production WSGI file missing"
    echo "   Please ensure wsgi_production.py exists"
    exit 1
fi

echo ""
echo "🎯 Next Steps:"
echo "=============="
echo ""
echo "1. 🗄️  Create Neon Database:"
echo "   - Go to https://neon.tech"
echo "   - Create new project"
echo "   - Copy connection string"
echo ""
echo "2. ⚙️  Deploy Backend on Render:"
echo "   - Go to https://render.com"
echo "   - Create new Web Service"
echo "   - Connect GitHub repo"
echo "   - Root Directory: finwise_backend"
echo "   - Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate"
echo "   - Start Command: gunicorn finwise_backend.wsgi_production:application --bind 0.0.0.0:8000"
echo ""
echo "3. 🌐 Deploy Frontend on Vercel:"
echo "   - Go to https://vercel.com"
echo "   - Import from GitHub"
echo "   - Root Directory: project_frontend/projectv2_v"
echo "   - Set VITE_API_BASE_URL to your Render API URL"
echo ""
echo "🔑 Environment Variables for Render:"
echo "===================================="
echo "DEBUG=False"
echo "SECRET_KEY=$SECRET_KEY"
echo "DATABASE_URL=<your-neon-connection-string>"
echo "GEMINI_API_KEY=<your-gemini-api-key>"
echo "ALLOWED_HOSTS=<your-render-service.onrender.com>"
echo "CORS_ALLOWED_ORIGINS=https://<your-frontend>.vercel.app"
echo ""
echo "📚 Full deployment guide: DEPLOYMENT_GUIDE.md"
echo ""
echo "🎉 Good luck with your deployment!" 