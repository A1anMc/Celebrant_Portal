import { api, apiRequest, tokenManager } from '@/lib/api';
import { LoginRequest, LoginResponse, User } from '@/types';

export const authService = {
  // Login user
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    try {
      // First, try to login and get tokens
      const response = await api.post('/api/auth/login', {
        email: credentials.email,
        password: credentials.password
      });

      const tokenData = response.data;
      
      // Store tokens
      tokenManager.setToken(tokenData.access_token);
      if (tokenData.refresh_token) {
        tokenManager.setRefreshToken(tokenData.refresh_token);
      }

      // Get user info
      try {
        const user = await authService.getCurrentUser();
        return { ...tokenData, user };
      } catch (error) {
        // If getting user info fails, clear tokens and throw error
        tokenManager.clearTokens();
        throw error;
      }
    } catch (error: any) {
      // Clear any existing tokens on login failure
      tokenManager.clearTokens();
      throw {
        message: error.response?.data?.detail || 'Login failed. Please check your credentials.',
        status: error.response?.status || 500
      };
    }
  },

  // Logout user
  logout: async (): Promise<void> => {
    try {
      // No change needed here, but good to keep.
      await api.post('/api/auth/logout');
    } catch (error) {
      console.warn('Logout API call failed, clearing tokens regardless:', error);
    } finally {
      tokenManager.clearTokens();
    }
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    return apiRequest<User>(() => api.get('/api/auth/me'));
  },

  // Register new user (admin only)
  register: async (userData: any): Promise<User> => {
    return apiRequest<User>(() => api.post('/api/auth/register', userData));
  },

  // Update user profile
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    // FIX: The backend endpoint is /me, not /profile.
    return apiRequest<User>(() => api.put('/api/auth/me', userData));
  },

  // Change password
  changePassword: async (passwordData: { current_password: string; new_password: string }): Promise<void> => {
    return apiRequest<void>(() => api.post('/api/auth/change-password', passwordData));
  },

  // Refresh token
  refreshToken: async (): Promise<{ access_token: string; token_type: string }> => {
    const refreshToken = tokenManager.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await api.post('/api/auth/refresh', {
      refresh_token: refreshToken
    });

    // Update stored access token
    if (response.data.access_token) {
      tokenManager.setToken(response.data.access_token);
    }

    return response.data;
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    const token = tokenManager.getToken();
    if (!token) return false;

    try {
      // Basic JWT expiration check
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp > currentTime;
    } catch {
      return false;
    }
  },

  // Get stored token
  getStoredToken: (): string | null => {
    return tokenManager.getToken();
  }
};

// Export token manager for use in API interceptors
export { tokenManager }; 