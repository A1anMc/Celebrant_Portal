// API utility functions for authenticated requests

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
};

// Generic authenticated fetch function
export const authenticatedFetch = async (url: string, options: RequestInit = {}) => {
  const headers = {
    ...getAuthHeaders(),
    ...options.headers,
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // Token is invalid, clear it and redirect to login
      localStorage.removeItem('authToken');
      window.location.href = '/login';
      throw new Error('Unauthorized - Please log in again');
    }

    return response;
  } catch (error) {
    if (error instanceof TypeError) {
      // Network error
      throw new Error('Network error - Please check your connection');
    }
    throw error;
  }
};

// Dashboard API calls
export const fetchDashboardData = async () => {
  const response = await authenticatedFetch('/api/dashboard');
  if (!response.ok) {
    throw new Error('Failed to fetch dashboard data');
  }
  return response.json();
};

// Notes API calls
export const addNote = async (content: string) => {
  const response = await authenticatedFetch('/api/notes', {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to add note');
  }
  
  return response.json();
}; 