// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

// Helper function for API calls with authentication
const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('access_token');
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  console.log(`API call to: ${API_BASE_URL}${endpoint}`);
  console.log('Request config:', config);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('API error:', errorData);
      throw new Error(errorData.error || errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('API response data:', data);
    return data;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// Authentication API
export const authAPI = {
  login: async (username: string, password: string) => {
    console.log('AuthAPI.login called with username:', username);
    const response = await fetch(`${API_BASE_URL}/token/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    console.log('Login response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('Login error:', errorData);
      throw new Error(errorData.detail || 'Login failed');
    }

    const data = await response.json();
    console.log('Login successful, storing tokens');
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    return data;
  },

  register: async (userData: {
    username: string;
    email: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
  }) => {
    console.log('AuthAPI.register called with userData:', userData);
    return apiCall('/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  getUserDetails: async () => {
    console.log('AuthAPI.getUserDetails called');
    return apiCall('/user/');
  },

  changePassword: async (passwordData: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }) => {
    console.log('AuthAPI.changePassword called');
    return apiCall('/change-password/', {
      method: 'POST',
      body: JSON.stringify(passwordData),
    });
  },

  refreshToken: async () => {
    console.log('AuthAPI.refreshToken called');
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(`${API_BASE_URL}/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return data;
  },

  logout: () => {
    console.log('AuthAPI.logout called');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// Profile API
export const profileAPI = {
  get: () => apiCall('/profile/'),
  update: (data: any) => apiCall('/profile/', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
};

// Dashboard API functions
export const dashboardAPI = {
  get: () => apiCall('/dashboard/'),
};

// Tax Savings API functions
export const taxSavingsAPI = {
  get: () => apiCall('/tax-savings/'),
};

// Benefits API functions
export const benefitsAPI = {
  get: async () => {
    console.log('BenefitsAPI.get called');
    try {
      const result = await apiCall('/benefits/');
      console.log('BenefitsAPI.get result:', result);
      return result;
    } catch (error) {
      console.error('BenefitsAPI.get error:', error);
      throw error;
    }
  },
};

// Reports API functions
export const reportsAPI = {
  get: () => apiCall('/reports/'),
  download: (reportId: number, reportType: string) => apiCall('/reports/', {
    method: 'POST',
    body: JSON.stringify({ report_id: reportId, report_type: reportType })
  })
};

// Chatbot API functions
export const chatbotAPI = {
  sendMessage: (message: string) => apiCall('/chatbot/', {
    method: 'POST',
    body: JSON.stringify({ message }),
  }),
};

// Financial Wisdom Library API functions
export const wisdomLibraryAPI = {
  get: () => apiCall('/wisdom-library/'),
};

export const booksAPI = {
  get: (params?: { search?: string; genre?: string; difficulty?: string; investment_level?: string }) => {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append('search', params.search);
    if (params?.genre) queryParams.append('genre', params.genre);
    if (params?.difficulty) queryParams.append('difficulty', params.difficulty);
    if (params?.investment_level) queryParams.append('investment_level', params.investment_level);
    
    const endpoint = `/books/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return apiCall(endpoint);
  },
  
  getDetail: (bookId: number) => apiCall(`/books/${bookId}/`),
};

export const readingHistoryAPI = {
  get: () => apiCall('/reading-history/'),
  
  update: (data: {
    book_id: number;
    status?: string;
    rating?: number;
    review?: string;
  }) => apiCall('/reading-history/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};

export const readingPreferencesAPI = {
  get: () => apiCall('/reading-preferences/'),
  
  update: (data: {
    preferred_genres?: string[];
    preferred_authors?: string[];
    preferred_topics?: string[];
    preferred_difficulty?: string;
    preferred_investment_level?: string;
    books_per_month?: number;
    reading_goal?: number;
  }) => apiCall('/reading-preferences/', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
};