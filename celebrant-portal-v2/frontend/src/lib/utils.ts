import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, parseISO, differenceInDays, isValid } from 'date-fns';

// Tailwind CSS class utility
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Date formatting utilities
export const formatDate = (date: string | Date, formatStr: string = 'dd/MM/yyyy'): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(dateObj)) return 'Invalid date';
    return format(dateObj, formatStr);
  } catch (error) {
    return 'Invalid date';
  }
};

export const formatDateTime = (date: string | Date): string => {
  return formatDate(date, 'dd/MM/yyyy HH:mm');
};

export const formatDateLong = (date: string | Date): string => {
  return formatDate(date, 'EEEE, dd MMMM yyyy');
};

export const getDaysUntil = (date: string | Date): number => {
  try {
    const targetDate = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(targetDate)) return 0;
    return differenceInDays(targetDate, new Date());
  } catch (error) {
    return 0;
  }
};

export const isDatePast = (date: string | Date): boolean => {
  return getDaysUntil(date) < 0;
};

export const isDateUpcoming = (date: string | Date, days: number = 30): boolean => {
  const daysUntil = getDaysUntil(date);
  return daysUntil >= 0 && daysUntil <= days;
};

// Currency formatting
export const formatCurrency = (amount: number, currency: string = 'AUD'): string => {
  return new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: currency,
  }).format(amount);
};

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-AU').format(num);
};

// String utilities
export const capitalize = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const generateInitials = (firstName: string, lastName: string): string => {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
};

export const formatFullName = (firstName: string, lastName: string): string => {
  return `${firstName} ${lastName}`;
};

export const formatCoupleNames = (partner1: { first_name: string; last_name: string }, partner2: { first_name: string; last_name: string }): string => {
  return `${formatFullName(partner1.first_name, partner1.last_name)} & ${formatFullName(partner2.first_name, partner2.last_name)}`;
};

// Status utilities
export const getStatusColor = (status: string): string => {
  const statusColors: Record<string, string> = {
    // Couple statuses
    enquiry: 'bg-blue-100 text-blue-800',
    booked: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-green-100 text-green-800',
    completed: 'bg-gray-100 text-gray-800',
    cancelled: 'bg-red-100 text-red-800',
    
    // Legal form statuses
    pending: 'bg-orange-100 text-orange-800',
    submitted: 'bg-blue-100 text-blue-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    
    // Invoice statuses
    draft: 'bg-gray-100 text-gray-800',
    sent: 'bg-blue-100 text-blue-800',
    paid: 'bg-green-100 text-green-800',
    overdue: 'bg-red-100 text-red-800',
  };
  
  return statusColors[status.toLowerCase()] || 'bg-gray-100 text-gray-800';
};

export const getUrgencyColor = (daysUntil: number): string => {
  if (daysUntil < 0) return 'bg-red-100 text-red-800'; // Overdue
  if (daysUntil <= 7) return 'bg-orange-100 text-orange-800'; // Urgent
  if (daysUntil <= 30) return 'bg-yellow-100 text-yellow-800'; // Soon
  return 'bg-green-100 text-green-800'; // On track
};

// Form validation utilities
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePhone = (phone: string): boolean => {
  const phoneRegex = /^(\+61|0)[2-9]\d{8}$/;
  return phoneRegex.test(phone.replace(/\s/g, ''));
};

export const validateABN = (abn: string): boolean => {
  const abnRegex = /^\d{11}$/;
  return abnRegex.test(abn.replace(/\s/g, ''));
};

// File utilities
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const getFileExtension = (filename: string): string => {
  return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2);
};

// URL utilities
export const downloadBlob = (blob: Blob, filename: string): void => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// Local storage utilities
export const setLocalStorage = (key: string, value: any): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(key, JSON.stringify(value));
  }
};

export const getLocalStorage = <T>(key: string, defaultValue: T): T => {
  if (typeof window !== 'undefined') {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error(`Error reading from localStorage key "${key}":`, error);
      return defaultValue;
    }
  }
  return defaultValue;
};

export const removeLocalStorage = (key: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(key);
  }
};

// Debounce utility
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}; 