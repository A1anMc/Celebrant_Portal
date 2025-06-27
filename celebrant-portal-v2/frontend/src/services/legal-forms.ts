import { api } from '@/lib/api';

export interface LegalForm {
  id: number;
  couple_id: number;
  form_type: 'noim' | 'marriage_certificate' | 'ceremony_script' | 'vows';
  status: 'draft' | 'pending' | 'submitted' | 'approved' | 'completed';
  form_data: Record<string, any>;
  generated_at: string;
  submitted_at?: string;
  deadline_date?: string;
  notes?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface CreateLegalFormRequest {
  couple_id: number;
  form_type: 'noim' | 'marriage_certificate' | 'ceremony_script' | 'vows';
  form_data: Record<string, any>;
  deadline_date?: string;
  notes?: string;
}

export interface LegalFormListResponse {
  forms: LegalForm[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface NOIMTrackingItem {
  id: number;
  couple_names: string;
  ceremony_date?: string;
  noim_status: string;
  deadline_date?: string;
  days_remaining?: number;
  is_overdue: boolean;
}

export const legalFormsService = {
  // Get all legal forms with optional filtering
  getForms: async (params: {
    couple_id?: number;
    form_type?: string;
    status?: string;
    page?: number;
    per_page?: number;
  } = {}): Promise<LegalFormListResponse> => {
    const searchParams = new URLSearchParams();
    
    if (params.couple_id) searchParams.append('couple_id', params.couple_id.toString());
    if (params.form_type) searchParams.append('form_type', params.form_type);
    if (params.status) searchParams.append('status', params.status);
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.per_page) searchParams.append('per_page', params.per_page.toString());

    const response = await api.get(`/api/legal-forms/?${searchParams.toString()}`);
    return response.data;
  },

  // Get a specific legal form by ID
  getFormById: async (id: number): Promise<LegalForm> => {
    const response = await api.get(`/api/legal-forms/${id}`);
    return response.data;
  },

  // Create a new legal form
  createForm: async (formData: CreateLegalFormRequest): Promise<LegalForm> => {
    const response = await api.post('/api/legal-forms/', formData);
    return response.data;
  },

  // Update an existing legal form
  updateForm: async (id: number, formData: Partial<CreateLegalFormRequest>): Promise<LegalForm> => {
    const response = await api.put(`/api/legal-forms/${id}`, formData);
    return response.data;
  },

  // Delete a legal form
  deleteForm: async (id: number): Promise<void> => {
    await api.delete(`/api/legal-forms/${id}`);
  },

  // FIX: Use actual backend endpoint for NOIM tracking
  getNOIMTracking: async (): Promise<NOIMTrackingItem[]> => {
    const response = await api.get('/api/legal-forms/noim-tracking');
    return response.data;
  },

  // Generate a specific type of form
  generateForm: async (coupleId: number, formType: string): Promise<LegalForm> => {
    const response = await api.post('/api/legal-forms/generate', {
      couple_id: coupleId,
      form_type: formType
    });
    return response.data;
  },

  // Submit a form (change status to submitted)
  submitForm: async (id: number): Promise<LegalForm> => {
    const response = await api.post(`/api/legal-forms/${id}/submit`);
    return response.data;
  },

  // Download a form as PDF
  downloadForm: async (id: number): Promise<Blob> => {
    const response = await api.get(`/api/legal-forms/${id}/download`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Get forms by couple ID
  getFormsByCouple: async (coupleId: number): Promise<LegalForm[]> => {
    const response = await api.get(`/api/legal-forms/?couple_id=${coupleId}&per_page=100`);
    return response.data.forms;
  },

  // Get pending forms (forms that need attention)
  getPendingForms: async (): Promise<LegalForm[]> => {
    const response = await api.get('/api/legal-forms/?status=pending&per_page=100');
    return response.data.forms;
  },

  // Get overdue forms
  getOverdueForms: async (): Promise<LegalForm[]> => {
    const response = await api.get('/api/legal-forms/overdue');
    return response.data;
  },

  // Helper function to get form statistics
  getFormStats: async () => {
    const response = await api.get('/api/legal-forms/?per_page=1000');
    const forms = response.data.forms;
    
    const stats = {
      total: forms.length,
      by_type: {} as Record<string, number>,
      by_status: {} as Record<string, number>,
      pending: 0,
      overdue: 0
    };

    const now = new Date();

    forms.forEach((form: LegalForm) => {
      // Count by type
      stats.by_type[form.form_type] = (stats.by_type[form.form_type] || 0) + 1;
      
      // Count by status
      stats.by_status[form.status] = (stats.by_status[form.status] || 0) + 1;
      
      // Count pending
      if (form.status === 'pending') {
        stats.pending++;
      }
      
      // Count overdue
      if (form.deadline_date && new Date(form.deadline_date) < now && form.status !== 'completed') {
        stats.overdue++;
      }
    });

    return stats;
  }
}; 