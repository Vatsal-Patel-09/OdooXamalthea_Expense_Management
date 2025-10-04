/**
 * API Configuration and Client
 * Connects frontend to Flask backend
 */

import axios, { AxiosInstance } from 'axios';

// Backend API Base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
});

// Request interceptor - Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const api = {
  // Authentication endpoints
  auth: {
    signup: (data: {
      email: string;
      password: string;
      name: string;
      company_name: string;
      currency?: string;
    }) => apiClient.post('/auth/signup', data),

    login: (data: { email: string; password: string }) =>
      apiClient.post('/auth/login', data),

    getCurrentUser: () => apiClient.get('/auth/me'),

    logout: () => {
      // Client-side logout (clear local storage)
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      return Promise.resolve();
    },
  },

  // User management endpoints (Admin only)
  users: {
    list: () => apiClient.get('/users'),
    get: (id: string) => apiClient.get(`/users/${id}`),
    create: (data: any) => apiClient.post('/users', data),
    update: (id: string, data: any) => apiClient.put(`/users/${id}`, data),
    delete: (id: string) => apiClient.delete(`/users/${id}`),
  },

  // Category endpoints
  categories: {
    list: () => apiClient.get('/categories'),
    get: (id: string) => apiClient.get(`/categories/${id}`),
    create: (data: any) => apiClient.post('/categories', data),
    update: (id: string, data: any) => apiClient.put(`/categories/${id}`, data),
    delete: (id: string) => apiClient.delete(`/categories/${id}`),
  },

  // Expense endpoints
  expenses: {
    list: (params?: any) => apiClient.get('/expenses', { params }),
    get: (id: string) => apiClient.get(`/expenses/${id}`),
    create: (data: any) => apiClient.post('/expenses', data),
    update: (id: string, data: any) => apiClient.put(`/expenses/${id}`, data),
    delete: (id: string) => apiClient.delete(`/expenses/${id}`),
    submit: (id: string) => apiClient.post(`/expenses/${id}/submit`),
    stats: () => apiClient.get('/expenses/stats'),
  },

  // File upload endpoints
  upload: {
    file: (formData: FormData) => 
      apiClient.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    delete: (filePath: string) => apiClient.delete(`/upload/${encodeURIComponent(filePath)}`),
    validate: (data: { filename: string; size: number }) => 
      apiClient.post('/upload/validate', data),
  },

  // Approval endpoints
  approvals: {
    list: (params?: any) => apiClient.get('/approvals', { params }),
    approve: (id: string, comments?: string) =>
      apiClient.post(`/approvals/${id}/approve`, { comments }),
    reject: (id: string, comments?: string) =>
      apiClient.post(`/approvals/${id}/reject`, { comments }),
  },

  // Countries and currencies
  countries: {
    list: () => apiClient.get('/countries'),
    currencies: () => apiClient.get('/currencies'),
    exchangeRates: (baseCurrency: string) => apiClient.get(`/exchange-rates/${baseCurrency}`),
    convert: (data: { amount: number; from: string; to: string }) =>
      apiClient.post('/convert', data),
  },

  // Health check
  health: () => apiClient.get('/health'),
};

export default apiClient;
