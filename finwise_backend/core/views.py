import os
import json
import random
from datetime import datetime, timedelta
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from .models import (
    UserProfile, DashboardSummary, Book, UserReadingPreference, 
    UserReadingHistory, BookRecommendation
)
from .serializers import (
    UserSerializer, UserProfileSerializer, DashboardSummarySerializer,
    BookSerializer, BookListSerializer, UserReadingPreferenceSerializer,
    UserReadingHistorySerializer, BookRecommendationSerializer,
    UserRegistrationSerializer
)
from .ai_service import ai_service

def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Finwise Backend API',
        'version': '1.0.0'
    })

def generate_tax_tips(profile):
    tips = []
    
    # Income-based tips
    if profile.income > 1000000:
        tips.append("Invest in ELSS for tax deduction under 80C.")
        tips.append("Consider NPS for additional tax benefits.")
    
    if profile.income > 500000:
        tips.append("Maximize 80C deductions with PPF and ELSS.")
    
    # Dependent-based tips
    if profile.dependents >= 2:
        tips.append("Claim deductions for dependent care under 80D.")
        tips.append("Consider health insurance for family tax benefits.")
    
    # Investment-based tips
    if profile.investment_amount < profile.income * 0.1:
        tips.append("Increase investment allocation to 10% of income.")
    
    # Savings-based tips
    if profile.monthly_savings < profile.income * 0.2:
        tips.append("Aim to save at least 20% of your monthly income.")
    
    # Emergency fund tips
    if profile.emergency_fund < profile.income * 0.06:
        tips.append("Build emergency fund equivalent to 6 months of income.")
    
    # Retirement planning
    if profile.retirement_savings < profile.income * 0.15:
        tips.append("Allocate 15% of income for retirement planning.")
    
    return tips

def calculate_savings_progress(profile):
    """Calculate savings progress and goals"""
    if profile.savings_goal > 0:
        progress = (profile.total_savings / profile.savings_goal) * 100
    else:
        progress = 0
    
    return {
        'total_savings': profile.total_savings,
        'monthly_savings': profile.monthly_savings,
        'savings_goal': profile.savings_goal,
        'progress_percentage': min(progress, 100)
    }

def get_gemini_tax_recommendations(profile):
    """Get AI-powered tax recommendations using Gemini"""
    try:
        # Convert profile to dictionary for AI service
        profile_dict = {
            'income': profile.income,
            'age': profile.age,
            'dependents': profile.dependents,
            'tax_deductions': profile.tax_deductions,
            'investment_amount': profile.investment_amount,
            'investment_types': profile.investment_types,
            'monthly_savings': profile.monthly_savings,
            'total_savings': profile.total_savings,
            'savings_goal': profile.savings_goal,
            'emergency_fund': profile.emergency_fund,
            'retirement_savings': profile.retirement_savings,
            'occupation': profile.occupation,
            'city': profile.city,
            'state': profile.state,
            'marital_status': profile.marital_status,
            'education': profile.education,
            'business_type': profile.business_type,
            'property_owned': profile.property_owned,
            'vehicle_owned': profile.vehicle_owned
        }
        
        # Use Gemini AI service
        response = ai_service.generate_tax_recommendations(profile_dict)
        print("Gemini Tax: Successfully generated response")
        return response
        
    except Exception as e:
        print(f"Gemini Tax API error: {e}")
        return generate_enhanced_tax_tips(profile)

def generate_enhanced_tax_tips(profile):
    """Generate enhanced tax tips based on profile data"""
    recommendations = []
    
    # Calculate potential savings
    current_tax_saved = profile.tax_deductions * 0.3  # Assuming 30% tax rate
    total_potential_savings = 0
    
    # Check if profile is complete (has meaningful data)
    is_profile_complete = (
        profile.income > 0 and 
        profile.age > 0 and 
        profile.name and 
        profile.email
    )
    
    if not is_profile_complete:
        # Provide onboarding recommendations for new users
        recommendations.append({
            "title": "Complete Your Profile",
            "description": "Please update your profile with accurate financial information to receive personalized recommendations.",
            "potential_saving": 0,
            "priority": "high",
            "category": "Profile Setup",
            "action": "Update Profile",
            "risk": "None",
            "returns": "Personalized Advice",
            "lock_in": "None"
        })
        
        recommendations.append({
            "title": "Basic Tax Planning",
            "description": "Start with basic tax-saving investments like PPF and ELSS once you have income details.",
            "potential_saving": 45000,  # Example: 1.5L * 0.3
            "priority": "medium",
            "category": "80C",
            "action": "Learn More",
            "risk": "Low to Medium",
            "returns": "7-15%",
            "lock_in": "3-15 years"
        })
        
        return {
            "recommendations": recommendations,
            "summary": {
                "total_potential_savings": 45000,
                "optimization_score": 30,
                "current_tax_saved": 0
            }
        }
    
    # Personalized recommendations based on actual profile data
    
    # Income-based recommendations
    if profile.income > 1000000:  # High income
        # ELSS for high earners
        elss_potential = min(150000 - profile.investment_amount, 50000)
        if elss_potential > 0:
            recommendations.append({
                "title": "Maximize ELSS Investment",
                "description": f"Invest ₹{elss_potential:,.0f} more in ELSS funds to reach the maximum limit.",
                "potential_saving": elss_potential * 0.3,
                "priority": "high",
                "category": "80C",
                "action": "Invest Now",
                "risk": "High",
                "returns": "12-15%",
                "lock_in": "3 years"
            })
            total_potential_savings += elss_potential * 0.3
        
        # NPS for high earners
        nps_potential = 50000
        recommendations.append({
            "title": "NPS Investment",
            "description": "Invest in NPS under Section 80CCD(1B) for additional ₹50,000 deduction.",
            "potential_saving": nps_potential * 0.3,
            "priority": "medium",
            "category": "NPS",
            "action": "Learn More",
            "risk": "Medium",
            "returns": "8-10%",
            "lock_in": "Till 60"
        })
        total_potential_savings += nps_potential * 0.3
        
    elif profile.income > 500000:  # Medium income
        # PPF for medium earners
        ppf_potential = min(150000 - profile.total_savings, 50000)
        if ppf_potential > 0:
            recommendations.append({
                "title": "Start PPF Investment",
                "description": f"Invest ₹{ppf_potential:,.0f} in PPF for tax-free returns and deductions.",
                "potential_saving": ppf_potential * 0.3,
                "priority": "high",
                "category": "80C",
                "action": "Open PPF Account",
                "risk": "Low",
                "returns": "7-8%",
                "lock_in": "15 years"
            })
            total_potential_savings += ppf_potential * 0.3
    
    else:  # Lower income
        # Basic savings for lower income
        basic_savings = min(50000, profile.income * 0.1)
        if basic_savings > 0:
            recommendations.append({
                "title": "Start Basic Savings",
                "description": f"Start with ₹{basic_savings:,.0f} in basic savings instruments.",
                "potential_saving": basic_savings * 0.1,  # Lower tax rate for lower income
                "priority": "medium",
                "category": "Basic Savings",
                "action": "Start Saving",
                "risk": "Low",
                "returns": "4-6%",
                "lock_in": "Flexible"
            })
            total_potential_savings += basic_savings * 0.1
    
    # Age-based recommendations
    if profile.age < 30:
        recommendations.append({
            "title": "Long-term Investment Strategy",
            "description": "You're young! Focus on equity-based investments for long-term wealth creation.",
            "potential_saving": 30000,
            "priority": "high",
            "category": "Investment Strategy",
            "action": "Plan Investments",
            "risk": "High",
            "returns": "12-18%",
            "lock_in": "5+ years"
        })
        total_potential_savings += 30000
    elif profile.age > 50:
        recommendations.append({
            "title": "Conservative Investment Approach",
            "description": "Focus on debt instruments and tax-saving bonds for stable returns.",
            "potential_saving": 25000,
            "priority": "high",
            "category": "Conservative",
            "action": "Review Portfolio",
            "risk": "Low",
            "returns": "6-8%",
            "lock_in": "3-5 years"
        })
        total_potential_savings += 25000
    
    # Dependent-based recommendations
    if profile.dependents >= 2:
        health_insurance_potential = 25000
        recommendations.append({
            "title": "Health Insurance for Family",
            "description": "Take health insurance for your family to claim deduction up to ₹25,000.",
            "potential_saving": health_insurance_potential * 0.3,
            "priority": "high",
            "category": "80D",
            "action": "Get Quote",
            "risk": "Low",
            "returns": "Tax Benefit",
            "lock_in": "1 year"
        })
        total_potential_savings += health_insurance_potential * 0.3
    elif profile.dependents == 1:
        health_insurance_potential = 15000
        recommendations.append({
            "title": "Individual Health Insurance",
            "description": "Consider health insurance for yourself to claim deduction up to ₹15,000.",
            "potential_saving": health_insurance_potential * 0.3,
            "priority": "medium",
            "category": "80D",
            "action": "Get Quote",
            "risk": "Low",
            "returns": "Tax Benefit",
            "lock_in": "1 year"
        })
        total_potential_savings += health_insurance_potential * 0.3
    
    # Emergency fund recommendations
    if profile.emergency_fund < profile.income * 0.06:
        emergency_potential = (profile.income * 0.06) - profile.emergency_fund
        recommendations.append({
            "title": "Build Emergency Fund",
            "description": f"Build emergency fund of ₹{emergency_potential:,.0f} for financial security.",
            "potential_saving": 0,  # No direct tax benefit
            "priority": "high",
            "category": "Emergency Fund",
            "action": "Start Saving",
            "risk": "Low",
            "returns": "4-6%",
            "lock_in": "Flexible"
        })
    
    # Retirement planning
    if profile.retirement_savings < profile.income * 0.15:
        retirement_potential = (profile.income * 0.15) - profile.retirement_savings
        recommendations.append({
            "title": "Retirement Planning",
            "description": f"Allocate ₹{retirement_potential:,.0f} annually for retirement planning.",
            "potential_saving": retirement_potential * 0.3,
            "priority": "medium",
            "category": "Retirement",
            "action": "Plan Retirement",
            "risk": "Medium",
            "returns": "8-12%",
            "lock_in": "Long-term"
        })
        total_potential_savings += retirement_potential * 0.3
    
    # Calculate optimization score based on profile completeness and recommendations
    optimization_score = min(30 + (len(recommendations) * 15) + (is_profile_complete * 20), 95)
    
    return {
        "recommendations": recommendations,
        "summary": {
            "total_potential_savings": total_potential_savings,
            "optimization_score": optimization_score,
            "current_tax_saved": current_tax_saved
        }
    }

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            if created:
                print(f"Created new profile for user: {self.request.user.username}")
            return profile
        except Exception as e:
            print(f"Error getting/creating profile for user {self.request.user.username}: {e}")
            raise

    def update(self, request, *args, **kwargs):
        try:
            print(f"Updating profile for user: {request.user.username}")
            print(f"Request data: {request.data}")
            
            # Get or create profile
            profile = self.get_object()
            
            # Update profile fields
            for field, value in request.data.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
            
            # Save the profile
            profile.save()
            print(f"Profile updated successfully for user: {request.user.username}")
            
            # Serialize and return
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
            
        except Exception as e:
            print(f"Error updating profile for user {request.user.username}: {e}")
            return Response(
                {'error': f'Failed to update profile: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        summary, _ = DashboardSummary.objects.get_or_create(user=request.user)
        
        # Generate personalized recommendations
        recommendations = generate_tax_tips(profile)
        summary.recommendations = ", ".join(recommendations)
        
        # Calculate savings progress
        savings_data = calculate_savings_progress(profile)
        summary.total_savings = savings_data['total_savings']
        summary.monthly_savings = savings_data['monthly_savings']
        summary.savings_goal = savings_data['savings_goal']
        summary.progress_percentage = savings_data['progress_percentage']
        
        summary.save()
        serializer = DashboardSummarySerializer(summary)
        return Response(serializer.data)

class TaxSavingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        
        # Get AI-powered recommendations
        tax_analysis = get_gemini_tax_recommendations(profile)
        
        # Calculate tax saving options based on profile
        tax_saving_options = self.calculate_tax_options(profile)
        
        return Response({
            'recommendations': tax_analysis.get('recommendations', []),
            'summary': tax_analysis.get('summary', {}),
            'tax_options': tax_saving_options,
            'profile_data': {
                'income': profile.income,
                'age': profile.age,
                'dependents': profile.dependents,
                'tax_deductions': profile.tax_deductions,
                'investment_amount': profile.investment_amount,
                'emergency_fund': profile.emergency_fund,
                'retirement_savings': profile.retirement_savings
            }
        })

    def calculate_tax_options(self, profile):
        """Calculate tax saving options based on profile"""
        return {
            '80C': [
                {
                    'name': 'ELSS Mutual Funds',
                    'limit': 150000,
                    'invested': min(profile.investment_amount, 150000),
                    'returns': '12-15%',
                    'risk': 'High',
                    'lockIn': '3 years',
                    'potential_saving': min(150000 - profile.investment_amount, 50000) * 0.3
                },
                {
                    'name': 'PPF',
                    'limit': 150000,
                    'invested': min(profile.total_savings * 0.3, 150000),
                    'returns': '7-8%',
                    'risk': 'Low',
                    'lockIn': '15 years',
                    'potential_saving': min(150000 - (profile.total_savings * 0.3), 50000) * 0.3
                },
                {
                    'name': 'NSC',
                    'limit': 100000,
                    'invested': min(profile.total_savings * 0.2, 100000),
                    'returns': '6-7%',
                    'risk': 'Low',
                    'lockIn': '5 years',
                    'potential_saving': min(100000 - (profile.total_savings * 0.2), 30000) * 0.3
                }
            ],
            '80D': [
                {
                    'name': 'Health Insurance Premium',
                    'limit': 25000,
                    'invested': min(profile.tax_deductions, 25000),
                    'returns': 'Tax Benefit',
                    'risk': 'Low',
                    'lockIn': '1 year',
                    'potential_saving': max(25000 - profile.tax_deductions, 0) * 0.3
                },
                {
                    'name': 'Parents Health Insurance',
                    'limit': 50000,
                    'invested': 0,
                    'returns': 'Tax Benefit',
                    'risk': 'Low',
                    'lockIn': '1 year',
                    'potential_saving': 50000 * 0.3
                }
            ],
            '80CCD': [
                {
                    'name': 'NPS Investment',
                    'limit': 50000,
                    'invested': 0,
                    'returns': '8-10%',
                    'risk': 'Medium',
                    'lockIn': 'Till 60',
                    'potential_saving': 50000 * 0.3
                }
            ]
        }

class ChatbotView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Handle chatbot messages with Gemini AI"""
        try:
            user_message = request.data.get('message', '')
            if not user_message:
                return Response({'error': 'Message is required'}, status=400)

            # Get user profile for context
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            
            # Get AI response using Gemini
            ai_response = self.get_gemini_chat_response(user_message, profile)
            
            return Response({
                'response': ai_response['response'],
                'suggestions': ai_response.get('suggestions', []),
                'confidence': ai_response.get('confidence', 0.8)
            })
            
        except Exception as e:
            print(f"Chatbot error: {e}")
            return Response({
                'response': "I'm having trouble processing your request right now. Please try again in a moment.",
                'suggestions': ["Tax savings tips", "Investment advice", "Government benefits"],
                'confidence': 0.5
            }, status=500)

    def get_gemini_chat_response(self, user_message, profile):
        """Get AI response using Gemini"""
        try:
            # Convert profile to dictionary for AI service
            profile_dict = {
                'income': profile.income,
                'age': profile.age,
                'investment_amount': profile.investment_amount,
                'dependents': profile.dependents,
                'occupation': profile.occupation,
                'city': profile.city,
                'state': profile.state,
                'emergency_fund': profile.emergency_fund,
                'retirement_savings': profile.retirement_savings,
                'tax_deductions': profile.tax_deductions
            }
            
            # Use Gemini AI service
            response = ai_service.generate_chat_response(user_message, profile_dict)
            print("Gemini Chat: Successfully generated response")
            return response
            
        except Exception as e:
            print(f"Gemini chat error: {e}")
            return self.get_fallback_response(user_message, profile)

    def get_enhanced_fallback_response(self, user_message, profile):
        """Enhanced fallback responses based on user profile"""
        message = user_message.lower()
        
        # Tax-related queries
        if any(word in message for word in ['tax', 'deduction', '80c', 'savings']):
            potential_savings = max(150000 - profile.investment_amount, 0) * 0.3
            return {
                "response": f"Based on your income of ₹{profile.income:,.0f}, here are tax-saving opportunities:\n\n• **ELSS Funds**: You can save ₹{potential_savings:,.0f} more by investing ₹{max(150000 - profile.investment_amount, 0):,.0f} in ELSS\n• **PPF**: Consider ₹{min(profile.income * 0.1, 150000):,.0f}/year for tax-free returns\n• **Health Insurance**: Get ₹25,000 deduction for family coverage\n• **NPS**: Additional ₹50,000 deduction under 80CCD(1B)\n\nWould you like detailed information about any of these options?",
                "suggestions": ["Tell me about ELSS funds", "How does NPS work?", "Health insurance benefits", "PPF vs other options"],
                "confidence": 0.9
            }
        
        # Investment queries
        if any(word in message for word in ['invest', 'mutual fund', 'stock', 'sip', 'portfolio']):
            recommended_sip = profile.income * 0.2
            return {
                "response": f"Great! Based on your income, here's a smart investment strategy:\n\n• **Monthly SIP**: ₹{recommended_sip:,.0f} (20% of income)\n• **Large Cap Funds**: 40% (₹{recommended_sip * 0.4:,.0f})\n• **Mid Cap Funds**: 30% (₹{recommended_sip * 0.3:,.0f})\n• **Small Cap Funds**: 20% (₹{recommended_sip * 0.2:,.0f})\n• **Debt Funds**: 10% (₹{recommended_sip * 0.1:,.0f})\n\nThis diversified approach balances risk and returns. Shall I suggest specific funds?",
                "suggestions": ["Best mutual funds for beginners", "How to start SIP?", "Risk assessment", "Portfolio review"],
                "confidence": 0.85
            }
        
        # Retirement planning
        if any(word in message for word in ['retirement', 'pension', 'future', 'planning']):
            years_to_retirement = 60 - profile.age
            monthly_needed = 8500  # Based on ₹2 crore goal
            return {
                "response": f"Let's plan your retirement! You have {years_to_retirement} years until 60.\n\n**Retirement Goal**: ₹2 crore by age 60\n**Monthly Investment Needed**: ₹{monthly_needed:,.0f}\n\n**Recommended Strategy**:\n• **PPF**: ₹1.5 lakh/year (₹12,500/month)\n• **Atal Pension Yojana**: ₹1,000/month\n• **Equity Mutual Funds**: ₹5,000/month\n\nThis will help you build a corpus of ₹2+ crores. Want a detailed retirement roadmap?",
                "suggestions": ["Create retirement roadmap", "PPF vs NPS comparison", "Pension scheme options", "Goal tracking"],
                "confidence": 0.9
            }
        
        # Government benefits
        if any(word in message for word in ['benefit', 'government', 'scheme', 'eligible', 'pmkisan']):
            return {
                "response": "You're eligible for several government benefits:\n\n• **PM-KISAN**: ₹6,000/year for farmers\n• **Ayushman Bharat**: ₹5 lakh health coverage\n• **PMAY**: Housing loan subsidy\n• **Mudra Loan**: Business funding up to ₹10 lakh\n• **PMJJBY**: ₹2 lakh life insurance for ₹330/year\n\nI can help you apply for any of these. Which one interests you?",
                "suggestions": ["How to apply for PM-KISAN?", "Ayushman Bharat eligibility", "Business loan requirements", "Insurance schemes"],
                "confidence": 0.8
            }
        
        # Emergency fund
        if any(word in message for word in ['emergency', 'savings', 'fund']):
            recommended_emergency = profile.income * 0.06  # 6 months
            current_shortfall = recommended_emergency - profile.emergency_fund
            return {
                "response": f"Emergency fund planning is crucial! Based on your income:\n\n• **Recommended Emergency Fund**: ₹{recommended_emergency:,.0f} (6 months of income)\n• **Current Emergency Fund**: ₹{profile.emergency_fund:,.0f}\n• **Shortfall**: ₹{current_shortfall:,.0f}\n\n**Action Plan**:\n• Save ₹{current_shortfall / 12:,.0f}/month for 1 year\n• Keep in high-yield savings account\n• Consider liquid mutual funds for better returns\n\nWould you like help setting up automatic transfers?",
                "suggestions": ["Set up automatic savings", "Best savings accounts", "Liquid fund options", "Emergency fund calculator"],
                "confidence": 0.85
            }
        
        # Default response
        return {
            "response": f"Hello! I'm your AI Financial Advisor. I can see you have ₹{profile.income:,.0f} annual income and ₹{profile.investment_amount:,.0f} in investments. How can I help you today? I can assist with tax planning, investments, government benefits, or retirement planning.",
            "suggestions": ["Tax optimization tips", "Investment strategy", "Government benefits", "Retirement planning"],
            "confidence": 0.7
        }

    def get_fallback_response(self, user_message, profile):
        """Basic fallback response"""
        return {
            "response": "I'm here to help with your financial goals! I can assist with tax planning, investments, government benefits, and retirement planning. What specific area would you like to discuss?",
            "suggestions": ["Tax savings tips", "Investment advice", "Government benefits", "Retirement planning"],
            "confidence": 0.6
        }
    



class BenefitsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        benefits = self.get_gemini_benefits(profile)
        return Response({
            'benefits': benefits
        })

    def get_gemini_benefits(self, profile):
        """Get AI-powered benefits recommendations using Gemini"""
        try:
            # Convert profile to dictionary for AI service
            profile_dict = {
                'income': profile.income,
                'age': profile.age,
                'dependents': profile.dependents,
                'occupation': profile.occupation,
                'investment_amount': profile.investment_amount,
                'emergency_fund': profile.emergency_fund,
                'retirement_savings': profile.retirement_savings,
                'tax_deductions': profile.tax_deductions,
                'city': profile.city,
                'state': profile.state,
                'marital_status': profile.marital_status,
                'education': profile.education,
                'business_type': profile.business_type
            }
            
            # Use Gemini AI service
            response = ai_service.generate_benefits_recommendations(profile_dict)
            print("Gemini Benefits: Successfully generated response")
            return response
            
        except Exception as e:
            print(f"Gemini benefits error: {e}")
            return self.get_fallback_benefits(profile)

    def get_fallback_benefits(self, profile):
        # Comprehensive fallback benefits list
        benefits = []
        
        # Income-based benefits
        if profile.income < 1200000:
            benefits.append({
                "name": "PM-KISAN",
                "description": "₹6,000/year income support for eligible farmers.",
                "eligibility_reason": "Income below ₹12 lakh.",
                "link": "https://pmkisan.gov.in",
                "amount": "₹6,000/year",
                "category": "Agriculture",
                "estimatedTime": "15-30 days"
            })
        
        if profile.income < 500000:
            benefits.append({
                "name": "Ayushman Bharat",
                "description": "₹5 lakh health insurance for low-income families.",
                "eligibility_reason": "Income below ₹5 lakh.",
                "link": "https://pmjay.gov.in",
                "amount": "₹5 lakh/year",
                "category": "Health",
                "estimatedTime": "Instant"
            })
        
        # Age-based benefits
        if profile.age >= 60:
            benefits.append({
                "name": "Senior Citizen Savings Scheme (SCSS)",
                "description": "High interest savings for seniors with 8.2% interest rate.",
                "eligibility_reason": "Age 60 or above.",
                "link": "https://www.nsiindia.gov.in",
                "amount": "8.2% interest",
                "category": "Savings",
                "estimatedTime": "7-15 days"
            })
        
        if profile.age >= 18 and profile.age <= 40:
            benefits.append({
                "name": "Atal Pension Yojana (APY)",
                "description": "Guaranteed pension scheme for unorganized sector workers.",
                "eligibility_reason": "Age between 18-40 years.",
                "link": "https://npscra.nsdl.co.in",
                "amount": "₹1,000-5,000/month",
                "category": "Pension",
                "estimatedTime": "15-30 days"
            })
        
        # Universal benefits
        benefits.append({
            "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
            "description": "₹2 lakh life insurance for ₹330/year.",
            "eligibility_reason": "Available to all savings account holders age 18-50.",
            "link": "https://www.jansuraksha.gov.in",
            "amount": "₹2 lakh coverage",
            "category": "Insurance",
            "estimatedTime": "Instant"
        })
        
        benefits.append({
            "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
            "description": "Accidental death and disability insurance for ₹12/year.",
            "eligibility_reason": "Available to all savings account holders age 18-70.",
            "link": "https://www.jansuraksha.gov.in",
            "amount": "₹2 lakh coverage",
            "category": "Insurance",
            "estimatedTime": "Instant"
        })
        
        # Investment-based benefits
        if profile.investment_amount < 150000:
            benefits.append({
                "name": "Public Provident Fund (PPF)",
                "description": "Long-term savings with tax benefits under 80C.",
                "eligibility_reason": "Available to all Indian residents.",
                "link": "https://www.nsiindia.gov.in",
                "amount": "7.1% interest",
                "category": "Savings",
                "estimatedTime": "7-15 days"
            })
        
        # Family-based benefits
        if profile.dependents > 0:
            benefits.append({
                "name": "Sukanya Samriddhi Yojana",
                "description": "Small savings scheme for girl child with attractive interest rates.",
                "eligibility_reason": "Available for girl child below 10 years.",
                "link": "https://www.nsiindia.gov.in",
                "amount": "8.2% interest",
                "category": "Savings",
                "estimatedTime": "7-15 days"
            })
        
        # Business/Employment benefits
        if profile.income < 800000:
            benefits.append({
                "name": "Pradhan Mantri Mudra Yojana",
                "description": "Collateral-free loans for micro enterprises.",
                "eligibility_reason": "For non-corporate, non-farm enterprises.",
                "link": "https://mudra.org.in",
                "amount": "Up to ₹10 lakh",
                "category": "Business",
                "estimatedTime": "30-45 days"
            })
        
        # Housing benefits
        if profile.income < 600000:
            benefits.append({
                "name": "Pradhan Mantri Awas Yojana (PMAY)",
                "description": "Housing assistance for economically weaker sections.",
                "eligibility_reason": "EWS/LIG families without pucca house.",
                "link": "https://pmaymis.gov.in",
                "amount": "Up to ₹2.67 lakh",
                "category": "Housing",
                "estimatedTime": "60-90 days"
            })
        
        return benefits

class ReportsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        reports = self.generate_user_reports(profile)
        return Response({
            'reports': reports,
            'stats': self.calculate_report_stats(profile)
        })

    def post(self, request):
        """Download a specific report"""
        try:
            report_id = request.data.get('report_id')
            report_type = request.data.get('report_type')
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            
            # Generate the specific report
            report_data = self.generate_specific_report(report_id, report_type, profile)
            
            # Create Excel-like data structure
            excel_data = self.convert_to_excel_format(report_data, report_type)
            
            return Response({
                'success': True,
                'report_data': report_data,
                'excel_data': excel_data,
                'filename': f"{report_data['title'].replace(' ', '_')}.xlsx",
                'message': 'Report generated successfully'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=400)

    def convert_to_excel_format(self, report_data, report_type):
        """Convert report data to Excel format"""
        if report_type == 'tax':
            return {
                'sheets': [
                    {
                        'name': 'Tax Summary',
                        'data': [
                            ['Tax Summary Report', ''],
                            ['', ''],
                            ['Total Income', f"₹{report_data['data']['total_income']:,.2f}"],
                            ['Tax Deductions', f"₹{report_data['data']['tax_deductions']:,.2f}"],
                            ['Potential Tax Savings', f"₹{report_data['data']['potential_savings']:,.2f}"],
                            ['Investment Amount', f"₹{report_data['data']['investment_amount']:,.2f}"],
                            ['80C Utilization', report_data['data']['80c_utilization']],
                            ['', ''],
                            ['Recommendations', ''],
                            ['1', report_data['data']['recommendations'][0]],
                            ['2', report_data['data']['recommendations'][1]],
                            ['3', report_data['data']['recommendations'][2]]
                        ]
                    }
                ]
            }
        elif report_type == 'investment':
            return {
                'sheets': [
                    {
                        'name': 'Investment Analysis',
                        'data': [
                            ['Investment Portfolio Analysis', ''],
                            ['', ''],
                            ['Total Investment', f"₹{report_data['data']['total_investment']:,.2f}"],
                            ['Investment Types', report_data['data']['investment_types']],
                            ['Monthly Savings', f"₹{report_data['data']['monthly_savings']:,.2f}"],
                            ['Savings Goal', f"₹{report_data['data']['savings_goal']:,.2f}"],
                            ['Progress Percentage', f"{report_data['data']['progress_percentage']:.1f}%"],
                            ['', ''],
                            ['Recommendations', ''],
                            ['1', report_data['data']['recommendations'][0]],
                            ['2', report_data['data']['recommendations'][1]],
                            ['3', report_data['data']['recommendations'][2]]
                        ]
                    }
                ]
            }
        else:
            return {
                'sheets': [
                    {
                        'name': 'Financial Health',
                        'data': [
                            ['Financial Health Assessment', ''],
                            ['', ''],
                            ['Emergency Fund', f"₹{report_data['data']['emergency_fund']:,.2f}"],
                            ['Retirement Savings', f"₹{report_data['data']['retirement_savings']:,.2f}"],
                            ['Total Savings', f"₹{report_data['data']['total_savings']:,.2f}"],
                            ['Monthly Savings', f"₹{report_data['data']['monthly_savings']:,.2f}"],
                            ['Financial Health Score', f"{report_data['data']['health_score']}/100"],
                            ['', ''],
                            ['Recommendations', ''],
                            ['1', report_data['data']['recommendations'][0]],
                            ['2', report_data['data']['recommendations'][1]],
                            ['3', report_data['data']['recommendations'][2]]
                        ]
                    }
                ]
            }

    def generate_specific_report(self, report_id, report_type, profile):
        """Generate a specific report with detailed data"""
        if report_type == 'tax':
            return {
                'title': 'Annual Tax Summary Report',
                'data': {
                    'total_income': profile.income,
                    'tax_deductions': profile.tax_deductions,
                    'potential_savings': profile.tax_deductions * 0.3,
                    'investment_amount': profile.investment_amount
                }
            }
        elif report_type == 'investment':
            return {
                'title': 'Investment Portfolio Analysis',
                'data': {
                    'total_investment': profile.investment_amount,
                    'investment_types': profile.investment_types,
                    'monthly_savings': profile.monthly_savings,
                    'savings_goal': profile.savings_goal,
                    'progress_percentage': (profile.total_savings / profile.savings_goal * 100) if profile.savings_goal > 0 else 0,
                    'recommendations': [
                        f"Allocate ₹{profile.income * 0.2:,.0f}/month for investments",
                        "Diversify across equity, debt, and gold",
                        "Consider SIP for systematic investing"
                    ]
                }
            }
        else:
            return {
                'title': 'Financial Health Assessment',
                'data': {
                    'emergency_fund': profile.emergency_fund,
                    'retirement_savings': profile.retirement_savings,
                    'total_savings': profile.total_savings,
                    'monthly_savings': profile.monthly_savings
                }
            }

    def calculate_financial_health_score(self, profile):
        """Calculate financial health score (0-100)"""
        score = 0
        
        # Emergency fund (25 points)
        if profile.emergency_fund >= profile.income * 0.06:
            score += 25
        elif profile.emergency_fund >= profile.income * 0.03:
            score += 15
        else:
            score += 5
            
        # Savings rate (25 points)
        savings_rate = (profile.monthly_savings / profile.income) * 100 if profile.income > 0 else 0
        if savings_rate >= 20:
            score += 25
        elif savings_rate >= 10:
            score += 15
        else:
            score += 5
            
        # Investment allocation (25 points)
        if profile.investment_amount >= profile.income * 0.1:
            score += 25
        elif profile.investment_amount >= profile.income * 0.05:
            score += 15
        else:
            score += 5
            
        # Retirement planning (25 points)
        if profile.retirement_savings >= profile.income * 0.15:
            score += 25
        elif profile.retirement_savings >= profile.income * 0.1:
            score += 15
        else:
            score += 5
            
        return score

    def generate_user_reports(self, profile):
        """Generate personalized reports based on user profile"""
        reports = []
        
        # Tax Summary Report
        reports.append({
            "id": 1,
            "title": "Annual Tax Summary Report",
            "description": f"Comprehensive overview of your tax savings and deductions for FY 2024-25",
            "type": "tax",
            "format": "PDF",
            "size": "2.3 MB",
            "date": "2024-07-15",
            "status": "ready",
            "color": "emerald",
            "data": {
                "total_income": profile.income,
                "tax_deductions": profile.tax_deductions,
                "potential_savings": profile.tax_deductions * 0.3,
                "investment_amount": profile.investment_amount
            }
        })
        
        # Investment Portfolio Report
        reports.append({
            "id": 2,
            "title": "Investment Portfolio Analysis",
            "description": "Detailed analysis of your investment performance and asset allocation",
            "type": "investment",
            "format": "PDF",
            "size": "1.8 MB",
            "date": "2024-07-14",
            "status": "ready",
            "color": "blue",
            "data": {
                "total_investment": profile.investment_amount,
                "investment_types": profile.investment_types,
                "monthly_savings": profile.monthly_savings,
                "savings_goal": profile.savings_goal
            }
        })
        
        # Benefits Report
        reports.append({
            "id": 3,
            "title": "Government Benefits Report",
            "description": "Summary of all government benefits you're eligible for",
            "type": "benefits",
            "format": "PDF",
            "size": "945 KB",
            "date": "2024-07-12",
            "status": "ready",
            "color": "purple",
            "data": {
                "age": profile.age,
                "income": profile.income,
                "dependents": profile.dependents
            }
        })
        
        # Financial Health Report
        reports.append({
            "id": 4,
            "title": "Financial Health Assessment",
            "description": "AI-generated financial health assessment and recommendations",
            "type": "investment",
            "format": "PDF",
            "size": "1.2 MB",
            "date": "2024-07-10",
            "status": "ready",
            "color": "indigo",
            "data": {
                "emergency_fund": profile.emergency_fund,
                "retirement_savings": profile.retirement_savings,
                "total_savings": profile.total_savings,
                "monthly_savings": profile.monthly_savings
            }
        })
        
        # Savings Progress Report
        reports.append({
            "id": 5,
            "title": "Savings Progress Report",
            "description": "Track your savings progress and goal achievement",
            "type": "investment",
            "format": "Excel",
            "size": "678 KB",
            "date": "2024-07-08",
            "status": "ready",
            "color": "green",
            "data": {
                "current_savings": profile.total_savings,
                "monthly_savings": profile.monthly_savings,
                "savings_goal": profile.savings_goal,
                "progress_percentage": (profile.total_savings / profile.savings_goal * 100) if profile.savings_goal > 0 else 0
            }
        })
        
        # Tax Deduction Report
        reports.append({
            "id": 6,
            "title": "Tax Deduction Breakdown",
            "description": "Detailed breakdown of all tax deductions under various sections",
            "type": "tax",
            "format": "Excel",
            "size": "456 KB",
            "date": "2024-07-05",
            "status": "ready",
            "color": "amber",
            "data": {
                "80c_deductions": min(profile.investment_amount, 150000),
                "80d_deductions": profile.tax_deductions,
                "total_deductions": profile.tax_deductions,
                "tax_saved": profile.tax_deductions * 0.3
            }
        })
        
        return reports

    def calculate_report_stats(self, profile):
        """Calculate report statistics"""
        return {
            "total_reports": 6,
            "tax_savings": f"₹{profile.tax_deductions * 0.3:,.0f}",
            "investment_performance": "+12.8%",
            "benefits_claimed": 8,
            "total_benefits_value": "₹2.3L"
        }

    def get_gemini_benefits(self, profile):
        """Get AI-powered benefits recommendations using Gemini"""
        try:
            # Convert profile to dictionary for AI service
            profile_dict = {
                'income': profile.income,
                'age': profile.age,
                'dependents': profile.dependents,
                'occupation': profile.occupation,
                'investment_amount': profile.investment_amount,
                'emergency_fund': profile.emergency_fund,
                'retirement_savings': profile.retirement_savings,
                'tax_deductions': profile.tax_deductions,
                'city': profile.city,
                'state': profile.state,
                'marital_status': profile.marital_status,
                'education': profile.education,
                'business_type': profile.business_type
            }
            
            # Use Gemini AI service
            response = ai_service.generate_benefits_recommendations(profile_dict)
            print("Gemini Reports Benefits: Successfully generated response")
            return response
            
        except Exception as e:
            print(f"Gemini Reports benefits error: {e}")
            return self.get_fallback_benefits(profile)

    def get_fallback_benefits(self, profile):
        # Comprehensive fallback benefits list
        benefits = []
        
        # Income-based benefits
        if profile.income < 1200000:
            benefits.append({
                "name": "PM-KISAN",
                "description": "₹6,000/year income support for eligible farmers.",
                "eligibility_reason": "Income below ₹12 lakh.",
                "link": "https://pmkisan.gov.in",
                "amount": "₹6,000/year",
                "category": "Agriculture",
                "estimatedTime": "15-30 days"
            })
        
        if profile.income < 500000:
            benefits.append({
                "name": "Ayushman Bharat",
                "description": "₹5 lakh health insurance for low-income families.",
                "eligibility_reason": "Income below ₹5 lakh.",
                "link": "https://pmjay.gov.in",
                "amount": "₹5 lakh/year",
                "category": "Health",
                "estimatedTime": "Instant"
            })
        
        # Age-based benefits
        if profile.age >= 60:
            benefits.append({
                "name": "Senior Citizen Savings Scheme (SCSS)",
                "description": "High interest savings for seniors with 8.2% interest rate.",
                "eligibility_reason": "Age 60 or above.",
                "link": "https://www.nsiindia.gov.in",
                "amount": "8.2% interest",
                "category": "Savings",
                "estimatedTime": "7-15 days"
            })
        
        if profile.age >= 18 and profile.age <= 40:
            benefits.append({
                "name": "Atal Pension Yojana (APY)",
                "description": "Guaranteed pension scheme for unorganized sector workers.",
                "eligibility_reason": "Age between 18-40 years.",
                "link": "https://npscra.nsdl.co.in",
                "amount": "₹1,000-5,000/month",
                "category": "Pension",
                "estimatedTime": "15-30 days"
            })
        
        # Universal benefits
        benefits.append({
            "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
            "description": "₹2 lakh life insurance for ₹330/year.",
            "eligibility_reason": "Available to all savings account holders age 18-50.",
            "link": "https://www.jansuraksha.gov.in",
            "amount": "₹2 lakh coverage",
            "category": "Insurance",
            "estimatedTime": "Instant"
        })
        
        benefits.append({
            "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
            "description": "Accidental death and disability insurance for ₹12/year.",
            "eligibility_reason": "Available to all savings account holders age 18-70.",
            "link": "https://www.jansuraksha.gov.in",
            "amount": "₹2 lakh coverage",
            "category": "Insurance",
            "estimatedTime": "Instant"
        })
        
        # Investment-based benefits
        if profile.investment_amount < 150000:
            benefits.append({
                "name": "Public Provident Fund (PPF)",
                "description": "Long-term savings with tax benefits under 80C.",
                "eligibility_reason": "Available to all Indian residents.",
                "link": "https://www.nsiindia.gov.in",
                "amount": "7.1% interest",
                "category": "Savings",
                "estimatedTime": "7-15 days"
            })
        
        # Family-based benefits
        if profile.dependents > 0:
            benefits.append({
                "name": "Sukanya Samriddhi Yojana",
                "description": "Small savings scheme for girl child with attractive interest rates.",
                "eligibility_reason": "Available for girl child below 10 years.",
                "link": "https://www.nsiindia.gov.in",
                "amount": "8.2% interest",
                "category": "Savings",
                "estimatedTime": "7-15 days"
            })
        
        # Business/Employment benefits
        if profile.income < 800000:
            benefits.append({
                "name": "Pradhan Mantri Mudra Yojana",
                "description": "Collateral-free loans for micro enterprises.",
                "eligibility_reason": "For non-corporate, non-farm enterprises.",
                "link": "https://mudra.org.in",
                "amount": "Up to ₹10 lakh",
                "category": "Business",
                "estimatedTime": "30-45 days"
            })
        
        # Housing benefits
        if profile.income < 600000:
            benefits.append({
                "name": "Pradhan Mantri Awas Yojana (PMAY)",
                "description": "Housing assistance for economically weaker sections.",
                "eligibility_reason": "EWS/LIG families without pucca house.",
                "link": "https://pmaymis.gov.in",
                "amount": "Up to ₹2.67 lakh",
                "category": "Housing",
                "estimatedTime": "60-90 days"
            })
        
        return benefits

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                name=f"{user.first_name} {user.last_name}".strip() or user.username,
                email=user.email
            )
            # Create dashboard summary
            DashboardSummary.objects.create(user=user)
            
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            return Response({
                'error': 'All password fields are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({
                'error': 'New passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(current_password):
            return Response({
                'error': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)

class WisdomLibraryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get personalized book recommendations and library overview"""
        try:
            user = request.user
            profile, _ = UserProfile.objects.get_or_create(user=user)
            preferences, _ = UserReadingPreference.objects.get_or_create(user=user)
            
            # Get personalized recommendations
            recommendations = self.get_personalized_recommendations(user, profile, preferences)
            
            # Get reading statistics
            reading_stats = self.get_reading_statistics(user)
            
            # Get recently viewed books
            recent_books = self.get_recent_books(user)
            
            return Response({
                'recommendations': recommendations,
                'reading_stats': reading_stats,
                'recent_books': recent_books,
                'user_preferences': UserReadingPreferenceSerializer(preferences).data
            })
        except Exception as e:
            print(f"Wisdom Library error: {e}")
            return Response({'error': 'Failed to load wisdom library'}, status=500)

    def get_personalized_recommendations(self, user, profile, preferences):
        """Generate personalized book recommendations using ML techniques"""
        try:
            # Get user's financial profile to determine relevant genres
            financial_genres = self.get_financial_genres(profile)
            
            # Get user's reading history
            reading_history = UserReadingHistory.objects.filter(user=user)
            
            # Combine user preferences with financial profile
            preferred_genres = list(set(preferences.preferred_genres + financial_genres))
            
            # Get books based on preferences and financial profile
            recommended_books = Book.objects.filter(
                Q(genre__in=preferred_genres) |
                Q(investment_level__in=self.get_investment_levels(profile))
            ).exclude(
                userreadinghistory__user=user,
                userreadinghistory__status='completed'
            ).distinct()
            
            # Apply ML-based scoring
            scored_books = []
            for book in recommended_books[:20]:  # Limit to top 20
                score = self.calculate_recommendation_score(book, user, profile, preferences)
                scored_books.append({
                    'book': BookListSerializer(book).data,
                    'score': score,
                    'reason': self.get_recommendation_reason(book, profile, preferences)
                })
            
            # Sort by score and return top recommendations
            scored_books.sort(key=lambda x: x['score'], reverse=True)
            return scored_books[:10]
            
        except Exception as e:
            print(f"Recommendation error: {e}")
            # Fallback to popular books
            return self.get_fallback_recommendations()

    def get_financial_genres(self, profile):
        """Determine relevant genres based on financial profile"""
        genres = []
        
        if profile.income > 1000000:  # High income
            genres.extend(['Business & Management', 'Investment'])
        elif profile.income > 500000:  # Medium income
            genres.extend(['Business & Management', 'Self-Help / Personal Growth'])
        else:  # Lower income
            genres.extend(['Self-Help / Personal Growth', 'Psychology'])
        
        if profile.age < 30:
            genres.append('Self-Help / Personal Growth')
        elif profile.age > 50:
            genres.extend(['Investment', 'Psychology'])
        
        if profile.investment_amount > 100000:
            genres.append('Investment')
        
        return list(set(genres))

    def get_investment_levels(self, profile):
        """Determine appropriate investment levels based on profile"""
        if profile.investment_amount > 500000:
            return ['Advanced', 'Intermediate']
        elif profile.investment_amount > 100000:
            return ['Intermediate', 'Beginner']
        else:
            return ['Beginner']

    def calculate_recommendation_score(self, book, user, profile, preferences):
        """Calculate ML-based recommendation score"""
        score = 0.0
        
        # Base score from book rating
        score += book.rating * 0.3
        
        # Genre preference score
        if book.genre in preferences.preferred_genres:
            score += 0.4
        
        # Financial relevance score
        financial_relevance = self.calculate_financial_relevance(book, profile)
        score += financial_relevance * 0.3
        
        # Popularity bonus
        score += book.popularity_score * 0.1
        
        return score

    def calculate_financial_relevance(self, book, profile):
        """Calculate how relevant a book is to user's financial situation"""
        relevance = 0.0
        
        # Income-based relevance
        if profile.income > 1000000 and book.genre == 'Business & Management':
            relevance += 0.5
        elif profile.income < 500000 and book.genre == 'Self-Help / Personal Growth':
            relevance += 0.5
        
        # Investment level relevance
        if profile.investment_amount > 500000 and book.investment_level == 'Advanced':
            relevance += 0.3
        elif profile.investment_amount < 100000 and book.investment_level == 'Beginner':
            relevance += 0.3
        
        # Age-based relevance
        if profile.age < 30 and book.genre == 'Self-Help / Personal Growth':
            relevance += 0.2
        elif profile.age > 50 and book.genre == 'Investment':
            relevance += 0.2
        
        return relevance

    def get_recommendation_reason(self, book, profile, preferences):
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        if book.genre in preferences.preferred_genres:
            reasons.append(f"Matches your preferred genre: {book.genre}")
        
        if profile.income > 1000000 and book.genre == 'Business & Management':
            reasons.append("Perfect for high-income professionals")
        elif profile.income < 500000 and book.genre == 'Self-Help / Personal Growth':
            reasons.append("Great for building financial foundation")
        
        if book.rating >= 4.0:
            reasons.append("Highly rated by readers")
        
        if book.investment_level == 'Beginner' and profile.investment_amount < 100000:
            reasons.append("Perfect for beginners")
        elif book.investment_level == 'Advanced' and profile.investment_amount > 500000:
            reasons.append("Advanced strategies for experienced investors")
        
        return " • ".join(reasons) if reasons else "Recommended based on your profile"

    def get_reading_statistics(self, user):
        """Get user's reading statistics"""
        history = UserReadingHistory.objects.filter(user=user)
        
        total_books = history.count()
        completed_books = history.filter(status='completed').count()
        currently_reading = history.filter(status='currently_reading').count()
        want_to_read = history.filter(status='want_to_read').count()
        
        avg_rating = history.filter(user_rating__isnull=False).aggregate(
            avg_rating=Avg('user_rating')
        )['avg_rating'] or 0.0
        
        return {
            'total_books': total_books,
            'completed_books': completed_books,
            'currently_reading': currently_reading,
            'want_to_read': want_to_read,
            'average_rating': round(avg_rating, 1),
            'completion_rate': round((completed_books / total_books * 100) if total_books > 0 else 0, 1)
        }

    def get_recent_books(self, user):
        """Get recently viewed or added books"""
        recent_history = UserReadingHistory.objects.filter(
            user=user
        ).order_by('-updated_at')[:5]
        
        return UserReadingHistorySerializer(recent_history, many=True).data

    def get_fallback_recommendations(self):
        """Fallback recommendations when ML fails"""
        popular_books = Book.objects.filter(rating__gte=4.0).order_by('-popularity_score')[:10]
        return [{
            'book': BookListSerializer(book).data,
            'score': book.rating,
            'reason': f"Popular {book.genre} book with {book.rating}★ rating"
        } for book in popular_books]

class BookListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get books with filtering and search"""
        try:
            search = request.GET.get('search', '')
            genre = request.GET.get('genre', '')
            difficulty = request.GET.get('difficulty', '')
            investment_level = request.GET.get('investment_level', '')
            
            books = Book.objects.all()
            
            if search:
                books = books.filter(
                    Q(title__icontains=search) |
                    Q(author__icontains=search) |
                    Q(genre__icontains=search)
                )
            
            if genre:
                books = books.filter(genre=genre)
            
            if difficulty:
                books = books.filter(difficulty_level=difficulty)
            
            if investment_level:
                books = books.filter(investment_level=investment_level)
            
            # Get available filters
            genres = Book.objects.values_list('genre', flat=True).distinct()
            difficulties = Book.objects.values_list('difficulty_level', flat=True).distinct()
            investment_levels = Book.objects.values_list('investment_level', flat=True).distinct()
            
            return Response({
                'books': BookListSerializer(books, many=True).data,
                'filters': {
                    'genres': list(genres),
                    'difficulties': list(difficulties),
                    'investment_levels': list(investment_levels)
                }
            })
        except Exception as e:
            print(f"Book list error: {e}")
            return Response({'error': 'Failed to load books'}, status=500)

class BookDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, book_id):
        """Get detailed book information"""
        try:
            book = Book.objects.get(id=book_id)
            user = request.user
            
            # Get user's interaction with this book
            user_history = UserReadingHistory.objects.filter(user=user, book=book).first()
            
            # Get similar books
            similar_books = Book.objects.filter(
                Q(genre=book.genre) | Q(investment_level=book.investment_level)
            ).exclude(id=book.id)[:6]
            
            return Response({
                'book': BookSerializer(book).data,
                'user_history': UserReadingHistorySerializer(user_history).data if user_history else None,
                'similar_books': BookListSerializer(similar_books, many=True).data
            })
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)
        except Exception as e:
            print(f"Book detail error: {e}")
            return Response({'error': 'Failed to load book details'}, status=500)

class UserReadingHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user's reading history"""
        try:
            history = UserReadingHistory.objects.filter(user=request.user).order_by('-updated_at')
            return Response(UserReadingHistorySerializer(history, many=True).data)
        except Exception as e:
            print(f"Reading history error: {e}")
            return Response({'error': 'Failed to load reading history'}, status=500)

    def post(self, request):
        """Add or update reading history"""
        try:
            book_id = request.data.get('book_id')
            status = request.data.get('status', 'want_to_read')
            rating = request.data.get('rating')
            review = request.data.get('review', '')
            
            book = Book.objects.get(id=book_id)
            history, created = UserReadingHistory.objects.get_or_create(
                user=request.user,
                book=book,
                defaults={'status': status}
            )
            
            if not created:
                history.status = status
                if rating:
                    history.user_rating = rating
                if review:
                    history.user_review = review
                history.save()
            
            return Response(UserReadingHistorySerializer(history).data)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)
        except Exception as e:
            print(f"Update reading history error: {e}")
            return Response({'error': 'Failed to update reading history'}, status=500)

class UserPreferencesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user's reading preferences"""
        try:
            preferences, _ = UserReadingPreference.objects.get_or_create(user=request.user)
            return Response(UserReadingPreferenceSerializer(preferences).data)
        except Exception as e:
            print(f"Get preferences error: {e}")
            return Response({'error': 'Failed to load preferences'}, status=500)

    def put(self, request):
        """Update user's reading preferences"""
        try:
            preferences, _ = UserReadingPreference.objects.get_or_create(user=request.user)
            
            # Update preferences
            if 'preferred_genres' in request.data:
                preferences.preferred_genres = request.data['preferred_genres']
            if 'preferred_authors' in request.data:
                preferences.preferred_authors = request.data['preferred_authors']
            if 'preferred_topics' in request.data:
                preferences.preferred_topics = request.data['preferred_topics']
            if 'preferred_difficulty' in request.data:
                preferences.preferred_difficulty = request.data['preferred_difficulty']
            if 'preferred_investment_level' in request.data:
                preferences.preferred_investment_level = request.data['preferred_investment_level']
            if 'books_per_month' in request.data:
                preferences.books_per_month = request.data['books_per_month']
            if 'reading_goal' in request.data:
                preferences.reading_goal = request.data['reading_goal']
            
            preferences.save()
            return Response(UserReadingPreferenceSerializer(preferences).data)
        except Exception as e:
            print(f"Update preferences error: {e}")
            return Response({'error': 'Failed to update preferences'}, status=500)
