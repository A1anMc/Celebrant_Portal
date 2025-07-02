'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';

interface User {
  id: number;
  email: string;
  full_name: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  refreshAccessToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshTokenTimeoutId, setRefreshTokenTimeoutId] = useState<NodeJS.Timeout>();
  const router = useRouter();

  const isAuthenticated = !!user;

  useEffect(() => {
    checkAuth();
    return () => {
      if (refreshTokenTimeoutId) {
        clearTimeout(refreshTokenTimeoutId);
      }
    };
  }, []);

  const setupRefreshTokenTimer = () => {
    // Refresh 1 minute before token expires
    const timeoutId = setTimeout(
      refreshAccessToken,
      (29 * 60 * 1000) // 29 minutes
    );
    setRefreshTokenTimeoutId(timeoutId);
  };

  const refreshAccessToken = async () => {
    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': Cookies.get('csrf_token') || '',
        },
      });

      if (response.ok) {
        const data = await response.json();
        Cookies.set('token', data.access_token, {
          secure: true,
          sameSite: 'Lax',
          expires: 30/1440, // 30 minutes
        });
        setupRefreshTokenTimer();
      } else {
        // If refresh fails, log out the user
        await logout();
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      await logout();
    }
  };

  const checkAuth = async () => {
    try {
      const response = await fetch('/api/auth/me', {
        credentials: 'include',
        headers: {
          'X-CSRF-Token': Cookies.get('csrf_token') || '',
        },
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setupRefreshTokenTimer();
      } else {
        Cookies.remove('token');
        Cookies.remove('refresh_token');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      Cookies.remove('token');
      Cookies.remove('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': Cookies.get('csrf_token') || '',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    
    // Set cookies with secure attributes
    Cookies.set('token', data.access_token, {
      secure: true,
      sameSite: 'Lax',
      expires: 30/1440, // 30 minutes
    });
    
    Cookies.set('refresh_token', data.refresh_token, {
      secure: true,
      sameSite: 'Lax',
      expires: 7, // 7 days
    });

    await checkAuth();
    setupRefreshTokenTimer();
    router.push('/dashboard');
  };

  const register = async (email: string, password: string, fullName: string) => {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': Cookies.get('csrf_token') || '',
      },
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    // Auto login after registration
    await login(email, password);
  };

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'X-CSRF-Token': Cookies.get('csrf_token') || '',
        },
      });
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setUser(null);
      Cookies.remove('token');
      Cookies.remove('refresh_token');
      Cookies.remove('csrf_token');
      if (refreshTokenTimeoutId) {
        clearTimeout(refreshTokenTimeoutId);
      }
      router.push('/login');
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        login,
        logout,
        register,
        refreshAccessToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}