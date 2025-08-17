from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView, ProfileView, DashboardView, TaxSavingsView, 
    ChatbotView, BenefitsView, ReportsView, UserRegistrationView, 
    UserDetailView, ChangePasswordView, WisdomLibraryView, BookListView,
    BookDetailView, UserReadingHistoryView, UserPreferencesView, health_check
)

urlpatterns = [
    # Health check endpoint
    path('health/', health_check, name='health_check'),
    
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Application endpoints
    path('profile/', ProfileView.as_view(), name='profile'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('tax-savings/', TaxSavingsView.as_view(), name='tax_savings'),
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
    path('benefits/', BenefitsView.as_view(), name='benefits'),
    path('reports/', ReportsView.as_view(), name='reports'),
    
    # Financial Wisdom Library endpoints
    path('wisdom-library/', WisdomLibraryView.as_view(), name='wisdom_library'),
    path('books/', BookListView.as_view(), name='book_list'),
    path('books/<int:book_id>/', BookDetailView.as_view(), name='book_detail'),
    path('reading-history/', UserReadingHistoryView.as_view(), name='reading_history'),
    path('reading-preferences/', UserPreferencesView.as_view(), name='reading_preferences'),
]
