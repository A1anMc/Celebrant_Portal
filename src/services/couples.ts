import { api, apiRequest } from '@/lib/api';
import { Couple, CoupleCreate, PaginatedResponse, SearchParams } from '@/types';

export const couplesService = {
  // Get all couples with pagination and search
  getCouples: async (params?: SearchParams): Promise<PaginatedResponse<Couple>> => {
    const searchParams = new URLSearchParams();
    
    if (params?.q) searchParams.append('q', params.q);
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.size) searchParams.append('size', params.size.toString());
    if (params?.sort_by) searchParams.append('sort_by', params.sort_by);
    if (params?.sort_order) searchParams.append('sort_order', params.sort_order);

    const queryString = searchParams.toString();
    const url = `/api/couples${queryString ? `?${queryString}` : ''}`;
    
    return apiRequest<PaginatedResponse<Couple>>(() => api.get(url));
  },

  // Get couple by ID
  getCouple: async (id: number): Promise<Couple> => {
    return apiRequest<Couple>(() => api.get(`/api/couples/${id}`));
  },

  // Create new couple
  createCouple: async (coupleData: CoupleCreate): Promise<Couple> => {
    return apiRequest<Couple>(() => api.post('/api/couples', coupleData));
  },

  // Update couple
  updateCouple: async (id: number, coupleData: Partial<CoupleCreate>): Promise<Couple> => {
    return apiRequest<Couple>(() => api.put(`/api/couples/${id}`, coupleData));
  },

  // Delete couple
  deleteCouple: async (id: number): Promise<void> => {
    return apiRequest<void>(() => api.delete(`/api/couples/${id}`));
  },

  // Search couples
  searchCouples: async (query: string): Promise<Couple[]> => {
    return apiRequest<Couple[]>(() => api.get(`/api/couples/search?q=${encodeURIComponent(query)}`));
  },

  // Get couples by status
  getCouplesByStatus: async (status: string): Promise<Couple[]> => {
    return apiRequest<Couple[]>(() => api.get(`/api/couples?status=${status}`));
  },

  // Get upcoming ceremonies
  getUpcomingCeremonies: async (days?: number): Promise<Couple[]> => {
    const params = days ? `?days=${days}` : '';
    return apiRequest<Couple[]>(() => api.get(`/api/couples/upcoming${params}`));
  },

  // Update couple status
  updateCoupleStatus: async (id: number, status: string): Promise<Couple> => {
    return apiRequest<Couple>(() => api.patch(`/api/couples/${id}/status`, { status }));
  },

  // Add payment to couple
  addPayment: async (id: number, amount: number, payment_method?: string): Promise<Couple> => {
    return apiRequest<Couple>(() => 
      api.post(`/api/couples/${id}/payment`, { 
        amount, 
        payment_method,
        payment_date: new Date().toISOString().split('T')[0]
      })
    );
  },

  // Get couple statistics
  getCoupleStats: async (): Promise<{
    total: number;
    by_status: Record<string, number>;
    by_type: Record<string, number>;
    monthly_bookings: Array<{ month: string; count: number }>;
  }> => {
    return apiRequest(() => api.get('/api/couples/stats'));
  },

  // Export couples data
  exportCouples: async (format: 'csv' | 'excel' = 'csv'): Promise<Blob> => {
    const response = await api.get(`/api/couples/export?format=${format}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Import couples data
  importCouples: async (file: File): Promise<{ success: number; errors: string[] }> => {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiRequest(() => 
      api.post('/api/couples/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    );
  },
}; 