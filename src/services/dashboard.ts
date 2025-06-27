// src/services/dashboard.ts
import { api, apiRequest } from '@/lib/api';
import { DashboardMetrics, UpcomingWeddingSummary } from '@/types';

export const dashboardService = {
  getDashboardMetrics: async (): Promise<DashboardMetrics> => {
    return apiRequest<DashboardMetrics>(() => api.get('/api/dashboard/metrics'));
  },
  getUpcomingWeddings: async (days: number = 30): Promise<UpcomingWeddingSummary> => {
    return apiRequest<UpcomingWeddingSummary>(() => api.get(`/api/dashboard/upcoming-weddings?days=${days}`));
  },
}; 