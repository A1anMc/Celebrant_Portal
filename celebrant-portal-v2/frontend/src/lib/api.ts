import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Extend the axios config type to include _retry
interface AxiosRequestConfigWithRetry extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

// Create axios instance
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true // Enable credentials for CORS
});

// Token management
export const tokenManager = {
  getToken: (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  },
  
  setToken: (token: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  },
  
  getRefreshToken: (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refresh_token');
    }
    return null;
  },
  
  setRefreshToken: (token: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('refresh_token', token);
    }
  },
  
  clearTokens: (): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = tokenManager.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfigWithRetry;
    
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = tokenManager.getRefreshToken();
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token: new_refresh_token } = response.data;
          tokenManager.setToken(access_token);
          tokenManager.setRefreshToken(new_refresh_token);
          
          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          tokenManager.clearTokens();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
      } else {
        // No refresh token, redirect to login
        tokenManager.clearTokens();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// API Response Types
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

// Generic API request wrapper
export const apiRequest = async <T>(
  request: () => Promise<any>
): Promise<T> => {
  try {
    const response = await request();
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw {
        message: error.response?.data?.detail || error.message,
        status: error.response?.status || 500,
        details: error.response?.data,
      } as ApiError;
    }
    throw error;
  }
};

export default api; 