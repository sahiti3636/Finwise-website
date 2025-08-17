# FinWise - Intelligent Financial Management Platform

A comprehensive financial management application with AI-powered recommendations, tax optimization, government benefits tracking, and personalized financial planning.

## Features

- **User Authentication**: Secure login/signup with JWT tokens
- **AI-Powered Financial Advisor**: Google Gemini AI integration for personalized financial advice
- **Tax Optimization**: Smart tax saving recommendations with estimated savings amounts
- **Government Benefits**: AI-powered eligibility checking and application guidance
- **Financial Dashboard**: Comprehensive overview of financial health and AI insights
- **Profile Management**: Detailed financial profile with comprehensive data
- **Report Generation**: Downloadable financial reports in Excel format
- **Admin Panel**: User management and system monitoring
- **Intelligent Chatbot**: Context-aware financial conversations powered by Gemini

## Tech Stack

### Backend
- **Django 5.0+**: Web framework
- **Django REST Framework**: API development
- **JWT Authentication**: Secure token-based authentication
- **SQLite/PostgreSQL**: Database
- **Google Gemini AI**: Advanced AI-powered financial recommendations
- **Python-dotenv**: Environment variable management


### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Framer Motion**: Animations
- **Zustand**: State management
- **React Router**: Navigation
- **Lucide React**: Icons

## AI Integration

FinWise features a sophisticated AI-powered financial advisor powered by **Google Gemini**. The AI system provides:

- **Personalized Financial Advice**: Context-aware recommendations based on user profile
- **Tax Optimization**: Section-wise tax savings strategies with estimated amounts
- **Government Benefits**: Eligibility analysis for Indian government schemes
- **Investment Guidance**: Portfolio recommendations based on risk profile
- **Retirement Planning**: Long-term financial planning strategies

### AI Features
- **Smart Context Understanding**: Analyzes income, age, dependents, and financial goals
- **Real-time Recommendations**: Instant, personalized financial advice
- **Fallback Systems**: Robust error handling with intelligent fallback responses
- **Multi-language Support**: Handles Indian financial context and terminology

### Getting Started with AI
1. **Get Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Configure Environment**: Set `GEMINI_API_KEY` in your `.env` file
3. **Test Integration**: Run `python test_gemini.py` to verify setup
4. **Start Using**: AI features are automatically available in the chatbot and recommendations

For detailed AI documentation, see [GEMINI_INTEGRATION.md](GEMINI_INTEGRATION.md).


