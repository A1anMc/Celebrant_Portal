// src/types/index.ts

// --- User and Authentication Types ---
// Matches backend schemas/auth.py
export interface User {
  id: number;
  email: string;
  name: string; // FIX: Was full_name
  role: 'admin' | 'celebrant' | 'assistant';
  is_active: boolean;
  phone?: string;
  business_name?: string;
  timezone: string;
  currency: string;
  created_at: string;
  last_login?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResponse extends TokenResponse {
  user: User;
}

// --- Couple and Ceremony Types ---
// Matches backend models/couple.py and schemas/couple.py
export interface Couple {
  id: number;
  // Partner 1
  partner_1_first_name: string;
  partner_1_last_name: string;
  partner_1_email?: string;
  partner_1_phone?: string;
  partner_1_date_of_birth?: string;
  partner_1_address?: string;
  // Partner 2
  partner_2_first_name: string;
  partner_2_last_name: string;
  partner_2_email?: string;
  partner_2_phone?: string;
  partner_2_date_of_birth?: string;
  partner_2_address?: string;

  status: 'inquiry' | 'consultation' | 'booked' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
  
  // Computed properties from backend
  full_names: string;
  primary_email?: string;
  primary_phone?: string;
}

export interface CoupleForm {
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
  status?: 'inquiry' | 'consultation' | 'booked' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
  estimated_guests?: number;
}

// --- Legal Forms Types ---
// Matches backend models/legal_form.py and schemas/legal_form.py
export interface LegalForm {
  id: number;
  form_type: 'noim' | 'birth_certificate' | 'divorce_decree' | 'death_certificate' | 'statutory_declaration' | 'other';
  status: 'required' | 'submitted' | 'approved' | 'expired' | 'rejected'; // FIX: Values updated
  deadline_date?: string;
  expiry_date?: string;
  submitted_date?: string;
  notes?: string;
  couple_id: number;
  ceremony_id?: number;

  // Computed properties from backend
  is_overdue: boolean;
  days_until_deadline?: number;
  is_expiring_soon: boolean;
}

// --- Dashboard Types ---
// These new types match what the backend dashboard endpoints actually return.
export interface DashboardMetrics {
  couples: {
    total: number;
    active: number;
    recent_inquiries: number;
  };
  ceremonies: {
    upcoming_30_days: number;
  };
  revenue: {
    total: number;
    monthly: number;
    outstanding_count: number;
    outstanding_amount: number;
    overdue_count: number;
    overdue_amount: number;
  };
  legal_forms: {
    urgent_attention: number;
  };
}

export interface UpcomingWedding {
    id: number;
    couple: {
        id: number;
        names: string;
        primary_email?: string;
        primary_phone?: string;
    };
    ceremony: {
        date: string;
        time: string;
        venue?: string;
        status: string;
        days_until: number;
    };
    total_fee: number;
}

export interface UpcomingWeddingSummary {
    summary: {
        total_ceremonies: number;
        this_week: number;
        next_week: number;
        this_month: number;
        total_revenue: number;
    };
    ceremonies: UpcomingWedding[];
}

// --- Search and Filter Types ---
export interface CoupleSearchParams {
  search?: string;
  status?: string;
  page?: number;
  per_page?: number;
}

// --- API Response Types ---
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface ErrorResponse {
  detail: string;
  error_code?: string;
} 