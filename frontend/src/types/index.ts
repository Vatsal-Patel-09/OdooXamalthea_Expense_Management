/**
 * TypeScript type definitions for the application
 */

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'manager' | 'employee';
  company_id: string;
  is_active: boolean;
  manager_id?: string;
  created_at?: string;
}

export interface Company {
  id: string;
  name: string;
  currency: string;
  created_by: string;
  created_at: string;
}

export interface Category {
  id: string;
  name: string;
  description?: string;
  company_id: string;
  is_active: boolean;
  created_at: string;
}

export interface Expense {
  id: string;
  user_id: string;
  company_id: string;
  category_id: string;
  amount: number;
  currency: string;
  expense_date: string;
  description?: string;
  receipt_url?: string;
  status: 'draft' | 'submitted' | 'approved' | 'rejected';
  submitted_at?: string;
  created_at: string;
  updated_at: string;
  // Joined data
  users?: {
    name: string;
    email: string;
  };
  categories?: {
    name: string;
  };
}

export interface Approval {
  id: string;
  expense_id: string;
  approver_id: string;
  approval_rule_id?: string;
  status: 'pending' | 'approved' | 'rejected';
  comments?: string;
  responded_at?: string;
  created_at: string;
  // Joined data
  expenses?: Expense;
}

export interface AuthResponse {
  status: string;
  message: string;
  data: {
    token: string;
    user: User;
  };
}

export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  message?: string;
  data?: T;
}
