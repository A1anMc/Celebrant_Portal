// Shared types for the Melbourne Celebrant Portal

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Couple {
  id: number;
  partner1_name: string;
  partner1_email: string;
  partner1_phone?: string;
  partner2_name: string;
  partner2_email: string;
  partner2_phone?: string;
  wedding_date: string;
  venue?: string;
  ceremony_type: string;
  status: 'Inquiry' | 'Booked' | 'Completed';
  notes?: string;
  celebrant_id: number;
  created_at: string;
  updated_at: string;
}

export interface Ceremony {
  id: number;
  couple_id: number;
  ceremony_script?: string;
  vows_partner1?: string;
  vows_partner2?: string;
  ring_exchange?: string;
  special_readings?: string;
  music_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: number;
  couple_id: number;
  invoice_number: string;
  amount: number;
  status: 'Draft' | 'Sent' | 'Paid' | 'Overdue';
  due_date?: string;
  paid_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface DashboardStats {
  total_couples: number;
  active_inquiries: number;
  booked_ceremonies: number;
  completed_ceremonies: number;
  total_revenue: number;
  this_month_revenue: number;
}
