import { api, apiRequest, tokenManager } from '@/lib/api';
import { LoginRequest, LoginResponse, User } from '@/types';

export const authService = {
  // Login user
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await api.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const loginData = response.data;
    
    // Store tokens
    tokenManager.setToken(loginData.access_token);
    if (loginData.refresh_token) {
      tokenManager.setRefreshToken(loginData.refresh_token);
    }

    return loginData;
  },

  // Logout user
  logout: async (): Promise<void> => {
    try {
      await api.post('/api/auth/logout');
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error);
    } finally {
      tokenManager.clearTokens();
    }
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    return apiRequest<User>(() => api.get('/api/auth/me'));
  },

  // Refresh token
  refreshToken: async (): Promise<LoginResponse> => {
    const refreshToken = tokenManager.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await api.post('/api/auth/refresh', {
      refresh_token: refreshToken,
    });

    const loginData = response.data;
    
    // Update stored tokens
    tokenManager.setToken(loginData.access_token);
    if (loginData.refresh_token) {
      tokenManager.setRefreshToken(loginData.refresh_token);
    }

    return loginData;
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    return tokenManager.getToken() !== null;
  },

  // Register new user (if needed)
  register: async (userData: {
    email: string;
    password: string;
    full_name: string;
    phone?: string;
    business_name?: string;
  }): Promise<User> => {
    return apiRequest<User>(() => api.post('/api/auth/register', userData));
  },

  // Update user profile
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    return apiRequest<User>(() => api.put('/api/auth/profile', userData));
  },

  // Change password
  changePassword: async (data: {
    current_password: string;
    new_password: string;
  }): Promise<void> => {
    return apiRequest<void>(() => api.post('/api/auth/change-password', data));
  },
}; 