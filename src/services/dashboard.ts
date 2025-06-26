import { api } from '@/lib/api';

export interface DashboardMetrics {
  total_couples: number;
  active_couples: number;
  completed_ceremonies: number;
  upcoming_ceremonies: number;
  pending_forms: number;
  revenue_this_month: number;
  revenue_total: number;
}

export interface UpcomingWedding {
  id: number;
  couple_names: string;
  ceremony_date: string;
  ceremony_time?: string;
  venue_name?: string;
  status: string;
  days_until: number;
}

export interface RecentActivity {
  id: number;
  type: 'couple_added' | 'form_generated' | 'ceremony_completed' | 'status_updated';
  description: string;
  timestamp: string;
  couple_id?: number;
  couple_names?: string;
}

export interface MonthlyRevenue {
  month: string;
  revenue: number;
  ceremonies: number;
}

export const dashboardService = {
  // FIX: Use actual backend endpoint /api/dashboard/metrics
  getMetrics: async (): Promise<DashboardMetrics> => {
    const response = await api.get('/api/dashboard/metrics');
    return response.data;
  },

  // FIX: Use actual backend endpoint /api/dashboard/upcoming-weddings
  getUpcomingWeddings: async (): Promise<UpcomingWedding[]> => {
    const response = await api.get('/api/dashboard/upcoming-weddings');
    return response.data;
  },

  // FIX: Use actual backend endpoint /api/dashboard/recent-activity
  getRecentActivity: async (): Promise<RecentActivity[]> => {
    const response = await api.get('/api/dashboard/recent-activity');
    return response.data;
  },

  // FIX: Use actual backend endpoint /api/dashboard/monthly-revenue
  getMonthlyRevenue: async (): Promise<MonthlyRevenue[]> => {
    const response = await api.get('/api/dashboard/monthly-revenue');
    return response.data;
  },

  // FIX: Use actual backend endpoint /api/dashboard/quick-stats
  getQuickStats: async () => {
    const response = await api.get('/api/dashboard/quick-stats');
    return response.data;
  },

  // Helper function to get all dashboard data at once
  getAllDashboardData: async () => {
    try {
      const [metrics, upcomingWeddings, recentActivity, monthlyRevenue] = await Promise.all([
        dashboardService.getMetrics(),
        dashboardService.getUpcomingWeddings(),
        dashboardService.getRecentActivity(),
        dashboardService.getMonthlyRevenue()
      ]);

      return {
        metrics,
        upcomingWeddings,
        recentActivity,
        monthlyRevenue
      };
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }
}; 