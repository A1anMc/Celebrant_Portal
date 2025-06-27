import { api, apiRequest } from '@/lib/api';
import { Couple, CoupleSearchParams, CoupleForm } from '@/types';

export interface CoupleListResponse {
  couples: Couple[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export const couplesService = {
  getCouples: async (params?: CoupleSearchParams): Promise<CoupleListResponse> => {
    // FIX: Use correct backend query parameter names and trailing slash
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.append('search', params.search);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.per_page) searchParams.append('per_page', params.per_page.toString());

    return apiRequest<CoupleListResponse>(() => api.get(`/api/couples/?${searchParams.toString()}`));
  },

  getCoupleById: async (id: number): Promise<Couple> => {
    return apiRequest<Couple>(() => api.get(`/api/couples/${id}/`));
  },

  createCouple: async (coupleData: CoupleForm): Promise<Couple> => {
    return apiRequest<Couple>(() => api.post('/api/couples/', coupleData));
  },

  updateCouple: async (id: number, coupleData: Partial<CoupleForm>): Promise<Couple> => {
    return apiRequest<Couple>(() => api.put(`/api/couples/${id}/`, coupleData));
  },

  deleteCouple: async (id: number): Promise<void> => {
    return apiRequest<void>(() => api.delete(`/api/couples/${id}/`));
  },

  // Helper functions using the main endpoint
  searchCouples: async (query: string): Promise<Couple[]> => {
    const response = await couplesService.getCouples({ search: query, per_page: 50 });
    return response.couples;
  },

  getCouplesByStatus: async (status: string): Promise<Couple[]> => {
    const response = await couplesService.getCouples({ status, per_page: 100 });
    return response.couples;
  }
}; 