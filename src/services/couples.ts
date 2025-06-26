import { api } from '@/lib/api';
import { Couple, CoupleStatus } from '@/types';

export interface CoupleSearchParams {
  search?: string;
  status?: CoupleStatus;
  page?: number;
  per_page?: number; // FIX: Changed from 'size' to 'per_page' to match backend
}

export interface CoupleListResponse {
  couples: Couple[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface CreateCoupleRequest {
  partner_1_first_name: string;
  partner_1_last_name: string;
  partner_1_email?: string;
  partner_1_phone?: string;
  partner_2_first_name: string;
  partner_2_last_name: string;
  partner_2_email?: string;
  partner_2_phone?: string;
  ceremony_date?: string;
  ceremony_time?: string;
  venue_name?: string;
  venue_address?: string;
  status?: CoupleStatus;
  notes?: string;
  estimated_guests?: number;
}

export const couplesService = {
  // FIX: Align with actual backend endpoint GET /api/couples/ with query parameters
  getCouples: async (params: CoupleSearchParams = {}): Promise<CoupleListResponse> => {
    const searchParams = new URLSearchParams();
    
    if (params.search) searchParams.append('search', params.search);
    if (params.status) searchParams.append('status', params.status);
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.per_page) searchParams.append('per_page', params.per_page.toString());

    const response = await api.get(`/api/couples/?${searchParams.toString()}`);
    return response.data;
  },

  getCoupleById: async (id: number): Promise<Couple> => {
    const response = await api.get(`/api/couples/${id}`);
    return response.data;
  },

  createCouple: async (coupleData: CreateCoupleRequest): Promise<Couple> => {
    const response = await api.post('/api/couples/', coupleData);
    return response.data;
  },

  updateCouple: async (id: number, coupleData: Partial<CreateCoupleRequest>): Promise<Couple> => {
    const response = await api.put(`/api/couples/${id}`, coupleData);
    return response.data;
  },

  deleteCouple: async (id: number): Promise<void> => {
    await api.delete(`/api/couples/${id}`);
  },

  // FIX: Remove non-existent endpoints and create functions that work with actual API
  getUpcomingCeremonies: async (): Promise<Couple[]> => {
    // Use the main couples endpoint with status filter
    const response = await api.get('/api/couples/?status=confirmed&per_page=10');
    return response.data.couples.filter((couple: Couple) => 
      couple.ceremony_date && new Date(couple.ceremony_date) > new Date()
    );
  },

  getCouplesByStatus: async (status: CoupleStatus): Promise<Couple[]> => {
    const response = await api.get(`/api/couples/?status=${status}&per_page=100`);
    return response.data.couples;
  },

  searchCouples: async (query: string): Promise<Couple[]> => {
    const response = await api.get(`/api/couples/?search=${encodeURIComponent(query)}&per_page=50`);
    return response.data.couples;
  },

  // Helper function to get couples statistics (derived from couples list)
  getCouplesStats: async () => {
    const response = await api.get('/api/couples/?per_page=1000'); // Get all couples
    const couples = response.data.couples;
    
    const stats = {
      total: couples.length,
      by_status: {} as Record<CoupleStatus, number>,
      upcoming_ceremonies: 0,
      this_month: 0
    };

    const now = new Date();
    const thisMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);

    couples.forEach((couple: Couple) => {
      // Count by status
      stats.by_status[couple.status] = (stats.by_status[couple.status] || 0) + 1;
      
      // Count upcoming ceremonies
      if (couple.ceremony_date && new Date(couple.ceremony_date) > now) {
        stats.upcoming_ceremonies++;
      }
      
      // Count this month's ceremonies
      if (couple.ceremony_date) {
        const ceremonyDate = new Date(couple.ceremony_date);
        if (ceremonyDate >= thisMonth && ceremonyDate < nextMonth) {
          stats.this_month++;
        }
      }
    });

    return stats;
  }
}; 