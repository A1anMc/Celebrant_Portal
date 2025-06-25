import { api, apiRequest } from '@/lib/api';
import { DashboardData, DashboardStats, UpcomingWedding } from '@/types';

export const dashboardService = {
  // Get complete dashboard data
  getDashboardData: async (): Promise<DashboardData> => {
    return apiRequest<DashboardData>(() => api.get('/api/dashboard'));
  },

  // Get dashboard statistics
  getStats: async (): Promise<DashboardStats> => {
    return apiRequest<DashboardStats>(() => api.get('/api/dashboard/stats'));
  },

  // Get upcoming weddings
  getUpcomingWeddings: async (limit: number = 5): Promise<UpcomingWedding[]> => {
    return apiRequest<UpcomingWedding[]>(() => 
      api.get(`/api/dashboard/upcoming-weddings?limit=${limit}`)
    );
  },

  // Get recent enquiries
  getRecentEnquiries: async (limit: number = 5) => {
    return apiRequest(() => api.get(`/api/dashboard/recent-enquiries?limit=${limit}`));
  },

  // Get pending tasks
  getPendingTasks: async () => {
    return apiRequest(() => api.get('/api/dashboard/pending-tasks'));
  },

  // Get revenue analytics
  getRevenueAnalytics: async (period: 'month' | 'quarter' | 'year' = 'month') => {
    return apiRequest(() => api.get(`/api/dashboard/revenue?period=${period}`));
  },

  // Get ceremony type breakdown
  getCeremonyTypeBreakdown: async () => {
    return apiRequest(() => api.get('/api/dashboard/ceremony-types'));
  },

  // Get monthly booking trends
  getBookingTrends: async (months: number = 12) => {
    return apiRequest(() => api.get(`/api/dashboard/booking-trends?months=${months}`));
  },

  // Get referral source analytics
  getReferralSources: async () => {
    return apiRequest(() => api.get('/api/dashboard/referral-sources'));
  },
}; 