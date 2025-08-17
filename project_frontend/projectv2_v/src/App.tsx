import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import TaxSavings from './pages/TaxSavings';
import Benefits from './pages/Benefits';
import Chatbot from './pages/Chatbot';
import WisdomLibrary from './pages/WisdomLibrary';
import Profile from './pages/Profile';
import Admin from './pages/Admin';
import Login from './pages/Login';
import Signup from './pages/Signup';
import { useAuthStore } from './store/authStore';

function App() {
  const { isAuthenticated, checkAuth, user, loading } = useAuthStore();
  const [error, setError] = useState<string | null>(null);
  const [authInitialized, setAuthInitialized] = useState(false);

  useEffect(() => {
    console.log('App component mounted');
    
    // Add a timeout to prevent infinite loading
    const timeoutId = setTimeout(() => {
      if (!authInitialized) {
        console.log('Auth check timeout - showing login page');
        setAuthInitialized(true);
      }
    }, 2000); // Reduced timeout to 2 seconds

    checkAuth()
      .then(() => {
        console.log('Auth check completed successfully');
        setAuthInitialized(true);
        clearTimeout(timeoutId);
      })
      .catch(error => {
        console.error('Auth check failed:', error);
        setError('Failed to check authentication');
        setAuthInitialized(true);
        clearTimeout(timeoutId);
      });

    return () => clearTimeout(timeoutId);
  }, [checkAuth, authInitialized]);

  console.log('App render - isAuthenticated:', isAuthenticated, 'loading:', loading, 'authInitialized:', authInitialized);

  // Show error if auth check failed
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4 text-4xl">Warning</div>
          <p className="text-gray-600 mb-4">Authentication Error</p>
          <p className="text-sm text-gray-500 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Show loading spinner while checking authentication (but with timeout)
  if (loading && !authInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading FinWise...</p>
          <p className="text-sm text-gray-500 mt-2">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // If auth is not initialized yet, show a simple loading
  if (!authInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        {isAuthenticated && <Navbar />}
        <AnimatePresence mode="wait">
          <Routes>
            <Route 
              path="/login" 
              element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />} 
            />
            <Route 
              path="/signup" 
              element={isAuthenticated ? <Navigate to="/dashboard" /> : <Signup />} 
            />
            <Route 
              path="/dashboard" 
              element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/profile" 
              element={isAuthenticated ? <Profile /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/tax-savings" 
              element={isAuthenticated ? <TaxSavings /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/chatbot" 
              element={isAuthenticated ? <Chatbot /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/benefits" 
              element={isAuthenticated ? <Benefits /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/wisdom-library" 
              element={isAuthenticated ? <WisdomLibrary /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/admin" 
              element={isAuthenticated && user?.role === 'admin' ? <Admin /> : <Navigate to="/dashboard" />} 
            />
            <Route 
              path="/" 
              element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} 
            />
          </Routes>
        </AnimatePresence>
      </div>
    </Router>
  );
}

export default App;