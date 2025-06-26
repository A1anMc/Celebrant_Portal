// Melbourne Celebrant Portal - Type Definitions
// Updated to match backend Pydantic schemas and SQLAlchemy models

// ===========================================
// USER TYPES
// ===========================================

export interface User {
  id: number;
  email: string;
  name: string; // FIX: Changed from full_name to name to match backend
  phone?: string;
  business_name?: string;
  role: 'admin' | 'celebrant' | 'user';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
}

// ===========================================
// COUPLE TYPES
// ===========================================

export type CoupleStatus = 'inquiry' | 'consultation' | 'booked' | 'confirmed' | 'completed' | 'cancelled';

// FIX: Updated to match backend flattened structure
export interface Couple {
  id: number;
  // Partner 1 fields
  partner_1_first_name: string;
  partner_1_last_name: string;
  partner_1_email?: string;
  partner_1_phone?: string;
  partner_1_address?: string;
  partner_1_date_of_birth?: string;
  partner_1_place_of_birth?: string;
  partner_1_occupation?: string;
  partner_1_nationality?: string;
  partner_1_marital_status?: string;
  partner_1_father_name?: string;
  partner_1_mother_name?: string;
  
  // Partner 2 fields
  partner_2_first_name: string;
  partner_2_last_name: string;
  partner_2_email?: string;
  partner_2_phone?: string;
  partner_2_address?: string;
  partner_2_date_of_birth?: string;
  partner_2_place_of_birth?: string;
  partner_2_occupation?: string;
  partner_2_nationality?: string;
  partner_2_marital_status?: string;
  partner_2_father_name?: string;
  partner_2_mother_name?: string;
  
  // Ceremony details
  ceremony_date?: string;
  ceremony_time?: string;
  venue_name?: string;
  venue_address?: string;
  venue_contact?: string;
  
  // Status and metadata
  status: CoupleStatus;
  notes?: string;
  estimated_guests?: number;
  special_requirements?: string;
  referral_source?: string;
  
  // System fields
  user_id: number;
  created_at: string;
  updated_at?: string;
}

// ===========================================
// LEGAL FORM TYPES
// ===========================================

export type LegalFormType = 'noim' | 'marriage_certificate' | 'ceremony_script' | 'vows';
export type LegalFormStatus = 'draft' | 'pending' | 'submitted' | 'approved' | 'completed';

export interface LegalForm {
  id: number;
  couple_id: number;
  form_type: LegalFormType;
  status: LegalFormStatus;
  form_data: Record<string, any>;
  generated_at: string;
  submitted_at?: string;
  deadline_date?: string;
  notes?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

// ===========================================
// CEREMONY TYPES
// ===========================================

export interface Ceremony {
  id: number;
  couple_id: number;
  ceremony_date: string;
  ceremony_time?: string;
  venue_name?: string;
  venue_address?: string;
  venue_contact?: string;
  ceremony_type?: string;
  estimated_guests?: number;
  special_requirements?: string;
  status: 'planned' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

// ===========================================
// INVOICE TYPES
// ===========================================

export type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';

export interface Invoice {
  id: number;
  couple_id: number;
  invoice_number: string;
  amount: number;
  status: InvoiceStatus;
  due_date?: string;
  paid_date?: string;
  notes?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

// ===========================================
// TEMPLATE TYPES
// ===========================================

export interface CeremonyTemplate {
  id: number;
  name: string;
  description?: string;
  template_type: 'ceremony' | 'vows' | 'reading' | 'blessing';
  content: string;
  is_default: boolean;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

// ===========================================
// TRAVEL LOG TYPES
// ===========================================

export interface TravelLog {
  id: number;
  couple_id?: number;
  ceremony_id?: number;
  travel_date: string;
  destination: string;
  distance_km: number;
  purpose: string;
  notes?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

// ===========================================
// API RESPONSE TYPES
// ===========================================

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

// ===========================================
// FORM TYPES
// ===========================================

export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  password: string;
  name: string;
  phone?: string;
  business_name?: string;
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
  status?: CoupleStatus;
  notes?: string;
  estimated_guests?: number;
}

// ===========================================
// DASHBOARD TYPES
// ===========================================

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

// ===========================================
// SEARCH AND FILTER TYPES
// ===========================================

export interface SearchParams {
  search?: string;
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface CoupleSearchParams extends SearchParams {
  status?: CoupleStatus;
}

export interface LegalFormSearchParams extends SearchParams {
  couple_id?: number;
  form_type?: LegalFormType;
  status?: LegalFormStatus;
}

// ===========================================
// UTILITY TYPES
// ===========================================

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Helper type for creating new entities (without system fields)
export type CreateEntity<T> = Omit<T, 'id' | 'created_at' | 'updated_at' | 'user_id'>;
export type UpdateEntity<T> = Partial<Omit<T, 'id' | 'created_at' | 'updated_at' | 'user_id'>>;

// ===========================================
// COMPONENT PROP TYPES
// ===========================================

export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, item: T) => React.ReactNode;
}

export interface FormFieldProps {
  label: string;
  name: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
  error?: string;
  value?: any;
  onChange?: (value: any) => void;
}

// ===========================================
// EXPORT ALL TYPES
// ===========================================

export type {
  // Main entities
  User,
  Couple,
  LegalForm,
  Ceremony,
  Invoice,
  CeremonyTemplate,
  TravelLog,
  
  // Enums
  CoupleStatus,
  LegalFormType,
  LegalFormStatus,
  InvoiceStatus,
  
  // API types
  ApiResponse,
  PaginatedResponse,
  ErrorResponse,
  
  // Form types
  LoginForm,
  RegisterForm,
  CoupleForm,
  
  // Dashboard types
  DashboardMetrics,
  UpcomingWedding,
  RecentActivity,
  
  // Search types
  SearchParams,
  CoupleSearchParams,
  LegalFormSearchParams,
  
  // Utility types
  Optional,
  RequiredFields,
  CreateEntity,
  UpdateEntity,
  
  // Component types
  BaseComponentProps,
  TableColumn,
  FormFieldProps
}; 