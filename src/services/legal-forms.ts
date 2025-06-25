import { api, apiRequest } from '@/lib/api';
import { LegalForm, LegalFormCreate, PaginatedResponse, SearchParams } from '@/types';

export const legalFormsService = {
  // Get all legal forms with pagination and search
  getLegalForms: async (params?: SearchParams): Promise<PaginatedResponse<LegalForm>> => {
    const searchParams = new URLSearchParams();
    
    if (params?.q) searchParams.append('q', params.q);
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.size) searchParams.append('size', params.size.toString());
    if (params?.sort_by) searchParams.append('sort_by', params.sort_by);
    if (params?.sort_order) searchParams.append('sort_order', params.sort_order);

    const queryString = searchParams.toString();
    const url = `/api/legal-forms${queryString ? `?${queryString}` : ''}`;
    
    return apiRequest<PaginatedResponse<LegalForm>>(() => api.get(url));
  },

  // Get legal form by ID
  getLegalForm: async (id: number): Promise<LegalForm> => {
    return apiRequest<LegalForm>(() => api.get(`/api/legal-forms/${id}`));
  },

  // Create new legal form
  createLegalForm: async (formData: LegalFormCreate): Promise<LegalForm> => {
    return apiRequest<LegalForm>(() => api.post('/api/legal-forms', formData));
  },

  // Update legal form
  updateLegalForm: async (id: number, formData: Partial<LegalFormCreate>): Promise<LegalForm> => {
    return apiRequest<LegalForm>(() => api.put(`/api/legal-forms/${id}`, formData));
  },

  // Delete legal form
  deleteLegalForm: async (id: number): Promise<void> => {
    return apiRequest<void>(() => api.delete(`/api/legal-forms/${id}`));
  },

  // Get forms by couple ID
  getFormsByCouple: async (coupleId: number): Promise<LegalForm[]> => {
    return apiRequest<LegalForm[]>(() => api.get(`/api/legal-forms/couple/${coupleId}`));
  },

  // Get forms by status
  getFormsByStatus: async (status: string): Promise<LegalForm[]> => {
    return apiRequest<LegalForm[]>(() => api.get(`/api/legal-forms?status=${status}`));
  },

  // Get pending NOIM forms
  getPendingNOIMForms: async (): Promise<LegalForm[]> => {
    return apiRequest<LegalForm[]>(() => api.get('/api/legal-forms?form_type=noim&status=pending'));
  },

  // Get expiring forms
  getExpiringForms: async (days: number = 30): Promise<LegalForm[]> => {
    return apiRequest<LegalForm[]>(() => api.get(`/api/legal-forms/expiring?days=${days}`));
  },

  // Update form status
  updateFormStatus: async (id: number, status: string, notes?: string): Promise<LegalForm> => {
    return apiRequest<LegalForm>(() => 
      api.patch(`/api/legal-forms/${id}/status`, { 
        status, 
        notes,
        ...(status === 'submitted' && { submission_date: new Date().toISOString().split('T')[0] }),
        ...(status === 'approved' && { approval_date: new Date().toISOString().split('T')[0] }),
      })
    );
  },

  // Upload form file
  uploadFormFile: async (id: number, file: File): Promise<LegalForm> => {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiRequest<LegalForm>(() => 
      api.post(`/api/legal-forms/${id}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    );
  },

  // Download form file
  downloadFormFile: async (id: number): Promise<Blob> => {
    const response = await api.get(`/api/legal-forms/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Send reminder for form
  sendReminder: async (id: number, message?: string): Promise<void> => {
    return apiRequest<void>(() => 
      api.post(`/api/legal-forms/${id}/reminder`, { message })
    );
  },

  // Get form statistics
  getFormStats: async (): Promise<{
    total: number;
    by_status: Record<string, number>;
    by_type: Record<string, number>;
    expiring_soon: number;
    overdue: number;
  }> => {
    return apiRequest(() => api.get('/api/legal-forms/stats'));
  },

  // Get NOIM deadline calculator
  calculateNOIMDeadline: async (ceremonyDate: string): Promise<{
    deadline: string;
    days_remaining: number;
    is_urgent: boolean;
    is_overdue: boolean;
  }> => {
    return apiRequest(() => 
      api.get(`/api/legal-forms/noim-deadline?ceremony_date=${ceremonyDate}`)
    );
  },

  // Get compliance checklist for couple
  getComplianceChecklist: async (coupleId: number): Promise<{
    couple_id: number;
    ceremony_date: string;
    required_forms: Array<{
      form_type: string;
      form_name: string;
      status: string;
      deadline?: string;
      is_urgent: boolean;
      is_complete: boolean;
    }>;
    compliance_score: number;
    missing_forms: string[];
    urgent_actions: string[];
  }> => {
    return apiRequest(() => api.get(`/api/legal-forms/compliance/${coupleId}`));
  },
}; 