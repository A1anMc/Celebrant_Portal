// User and Authentication Types
export interface User {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  business_name?: string;
  business_address?: string;
  abn?: string;
  role: 'admin' | 'celebrant' | 'assistant';
  is_active: boolean;
  created_at: string;
  updated_at: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  notifications_enabled: boolean;
  default_ceremony_duration: number;
  default_travel_rate: number;
  timezone: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// Couple and Ceremony Types
export interface Partner {
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  address?: string;
  date_of_birth?: string;
}

export interface Couple {
  id: number;
  partner1: Partner;
  partner2: Partner;
  ceremony_date?: string;
  ceremony_time?: string;
  ceremony_venue?: string;
  ceremony_address?: string;
  ceremony_type: 'wedding' | 'commitment' | 'renewal' | 'naming' | 'funeral';
  status: 'enquiry' | 'booked' | 'confirmed' | 'completed' | 'cancelled';
  package_type?: string;
  total_fee?: number;
  deposit_paid?: number;
  balance_due?: number;
  notes?: string;
  contact_preference: 'email' | 'phone' | 'both';
  referral_source?: string;
  special_requirements?: string;
  guest_count?: number;
  rehearsal_required: boolean;
  rehearsal_date?: string;
  rehearsal_time?: string;
  created_at: string;
  updated_at: string;
  user_id: number;
}

export interface CoupleCreate {
  partner1: Partner;
  partner2: Partner;
  ceremony_date?: string;
  ceremony_time?: string;
  ceremony_venue?: string;
  ceremony_address?: string;
  ceremony_type: 'wedding' | 'commitment' | 'renewal' | 'naming' | 'funeral';
  status?: 'enquiry' | 'booked' | 'confirmed' | 'completed' | 'cancelled';
  package_type?: string;
  total_fee?: number;
  deposit_paid?: number;
  balance_due?: number;
  notes?: string;
  contact_preference?: 'email' | 'phone' | 'both';
  referral_source?: string;
  special_requirements?: string;
  guest_count?: number;
  rehearsal_required?: boolean;
  rehearsal_date?: string;
  rehearsal_time?: string;
}

// Legal Forms Types
export interface LegalForm {
  id: number;
  couple_id: number;
  form_type: 'noim' | 'marriage_certificate' | 'statutory_declaration' | 'other';
  form_name: string;
  status: 'pending' | 'submitted' | 'approved' | 'rejected';
  submission_date?: string;
  approval_date?: string;
  expiry_date?: string;
  file_path?: string;
  notes?: string;
  reminder_sent: boolean;
  created_at: string;
  updated_at: string;
  couple?: Couple;
}

export interface LegalFormCreate {
  couple_id: number;
  form_type: 'noim' | 'marriage_certificate' | 'statutory_declaration' | 'other';
  form_name: string;
  status?: 'pending' | 'submitted' | 'approved' | 'rejected';
  submission_date?: string;
  approval_date?: string;
  expiry_date?: string;
  file_path?: string;
  notes?: string;
}

// Template Types
export interface CeremonyTemplate {
  id: number;
  name: string;
  description?: string;
  category: 'wedding' | 'commitment' | 'renewal' | 'naming' | 'funeral';
  content: string;
  is_default: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
  user_id: number;
}

export interface TemplateCreate {
  name: string;
  description?: string;
  category: 'wedding' | 'commitment' | 'renewal' | 'naming' | 'funeral';
  content: string;
  is_default?: boolean;
}

// Invoice Types
export interface InvoiceItem {
  id: number;
  description: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  gst_amount: number;
}

export interface Invoice {
  id: number;
  couple_id: number;
  invoice_number: string;
  issue_date: string;
  due_date: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  subtotal: number;
  gst_amount: number;
  total_amount: number;
  paid_amount: number;
  payment_date?: string;
  payment_method?: string;
  notes?: string;
  items: InvoiceItem[];
  created_at: string;
  updated_at: string;
  couple?: Couple;
}

export interface InvoiceCreate {
  couple_id: number;
  due_date: string;
  items: {
    description: string;
    quantity: number;
    unit_price: number;
  }[];
  notes?: string;
}

// Dashboard Types
export interface DashboardStats {
  total_couples: number;
  upcoming_ceremonies: number;
  pending_noim_forms: number;
  total_revenue: number;
  monthly_revenue: number;
  overdue_invoices: number;
}

export interface UpcomingWedding {
  id: number;
  couple_names: string;
  ceremony_date: string;
  ceremony_time?: string;
  venue?: string;
  days_until: number;
  status: string;
}

export interface DashboardData {
  stats: DashboardStats;
  upcoming_weddings: UpcomingWedding[];
  recent_enquiries: Couple[];
  pending_tasks: {
    noim_forms: LegalForm[];
    overdue_invoices: Invoice[];
  };
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface SearchParams {
  q?: string;
  page?: number;
  size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// Form Types
export interface FormError {
  field: string;
  message: string;
}

export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

// UI State Types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, item: T) => React.ReactNode;
}

export interface FilterOption {
  value: string;
  label: string;
}

// Travel and Reports (for future implementation)
export interface TravelLog {
  id: number;
  couple_id: number;
  date: string;
  destination: string;
  distance_km: number;
  cost: number;
  notes?: string;
}

export interface ReportData {
  period: string;
  total_ceremonies: number;
  total_revenue: number;
  average_fee: number;
  top_referral_sources: { source: string; count: number }[];
  monthly_breakdown: { month: string; ceremonies: number; revenue: number }[];
} 