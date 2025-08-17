# Finwise - AI-Powered Financial Advisor

> **Status: Production Deployed** | **Backend**: Render | **Frontend**: Vercel | **Database**: Neon PostgreSQL

A comprehensive financial advisory platform that combines AI-powered insights with personalized financial planning tools. Built with Django, React, and enhanced with Java microservices.

## Features

- **AI-Powered Recommendations**: Google Gemini AI integration for personalized financial advice
- **Financial Dashboard**: Comprehensive overview of income, savings, and investments
- **Tax Optimization**: Smart tax-saving strategies and deductions
- **Wisdom Library**: Curated financial books and resources
- **AI Chatbot**: Interactive financial guidance
- **Investment Tracking**: Monitor and analyze investment performance
- **Goal Setting**: Personalized financial goal planning

## Architecture

### Backend (Django + Python)
- **Framework**: Django 5 + Django REST Framework
- **Authentication**: JWT-based secure authentication
- **Database**: PostgreSQL (Neon) with SQLite for development
- **AI Integration**: Google Gemini API for intelligent recommendations
- **Deployment**: Render (Production), Local development support

### Frontend (React + TypeScript)
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS for modern, responsive design
- **State Management**: Zustand for efficient state handling
- **Deployment**: Vercel with automatic deployments

### Java Microservices
- **BookCoverService**: Java implementation of the Python book cover service
- **Technology**: Java 11+, Maven, built-in HTTP client
- **Features**: Multi-source book cover fetching with fallbacks
- **Purpose**: Demonstrates code conversion capabilities and Java integration

## Deployment Status

### Production Environment
- **Backend API**: [https://finwise-api.onrender.com](https://finwise-api.onrender.com)
- **Frontend**: [https://finwise-website.vercel.app](https://finwise-website.vercel.app)
- **Database**: Neon PostgreSQL (Serverless)
- **Health Check**: `/api/health/` endpoint for monitoring

### Deployment Stack
- **Backend**: Render (Web Service)
- **Frontend**: Vercel (Automatic deployments)
- **Database**: Neon (Serverless PostgreSQL)
- **CDN**: Vercel Edge Network
- **SSL**: Automatic HTTPS provisioning

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (for production)
- Google Gemini API key

### Backend Setup
```bash
cd finwise_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Environment Configuration
cp .env.example .env
# Edit .env with your configuration

# Database Setup
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run Development Server
python manage.py runserver
```

### Frontend Setup
```bash
cd project_frontend/projectv2_v
npm install

# Environment Configuration
# Create .env file with:
# VITE_API_BASE_URL=http://localhost:8000/api

# Development
npm run dev

# Production Build
npm run build
```

## Environment Variables

### Backend (.env)
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@host:port/database
GEMINI_API_KEY=your-gemini-api-key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```env
VITE_API_BASE_URL=https://your-backend-url.com/api
```

## API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `POST /api/token/` - User login
- `POST /api/token/refresh/` - Refresh token
- `GET /api/user/` - Get user details

### Core Features
- `GET /api/dashboard/` - Financial dashboard
- `GET /api/tax-savings/` - Tax optimization
- `GET /api/benefits/` - Government benefits
- `POST /api/chatbot/` - AI financial advisor
- `GET /api/wisdom-library/` - Financial resources

### Health & Monitoring
- `GET /api/health/` - Service health check

## Java Integration

The project includes a **Java microservice** (`BookCoverService`) that demonstrates:

- **Code Conversion**: Python → Java implementation
- **Multi-Source Integration**: Google Books + OpenLibrary APIs
- **Fallback Strategy**: Graceful degradation with placeholder generation
- **Production Ready**: Built with Java best practices

### Java Features
- **No External Dependencies**: Uses only Java standard library
- **Functional Interfaces**: Modern Java 8+ patterns
- **Error Handling**: Comprehensive exception management
- **Performance**: Optimized HTTP requests and response parsing

## Project Structure

```
finwise_project/
├── finwise_backend/          # Django backend
│   ├── core/                # Main application logic
│   ├── finwise_backend/     # Django project settings
│   ├── requirements.txt     # Python dependencies
│   └── manage.py           # Django management
├── project_frontend/        # React frontend
│   └── projectv2_v/        # Main frontend application
│       ├── src/            # Source code
│       ├── package.json    # Node dependencies
│       └── vite.config.ts  # Vite configuration
└── README.md               # This file
```

## Production Deployment

### Backend (Render)
1. **Connect GitHub repository**
2. **Set Root Directory**: `finwise_backend`
3. **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
4. **Start Command**: `gunicorn finwise_backend.wsgi:application --bind 0.0.0.0:8000`
5. **Environment Variables**: Set all required variables

### Frontend (Vercel)
1. **Import from GitHub**
2. **Root Directory**: `project_frontend/projectv2_v`
3. **Build Command**: `npm run build`
4. **Output Directory**: `dist`
5. **Environment Variables**: Set `VITE_API_BASE_URL`

### Database (Neon)
1. **Create PostgreSQL project**
2. **Copy connection string**
3. **Set as `DATABASE_URL`** in backend environment

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **CORS Protection**: Configured for production domains
- **Environment Variables**: Sensitive data protection
- **HTTPS Enforcement**: Automatic SSL in production
- **Input Validation**: Comprehensive data validation

## Performance & Scalability

- **CDN Distribution**: Vercel Edge Network
- **Database Optimization**: Connection pooling and health checks
- **Static File Handling**: WhiteNoise for efficient serving
- **API Rate Limiting**: Respectful API usage
- **Caching Strategy**: Optimized response times

## Testing & Quality

- **TypeScript**: Full type safety in frontend
- **ESLint**: Code quality enforcement
- **API Testing**: Comprehensive endpoint testing
- **Error Handling**: Graceful error management
- **Logging**: Production-ready logging system



