"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export default function NewExpensePage() {
  const router = useRouter();
  const { user } = useAuth();
  
  const [categories, setCategories] = useState<any[]>([]);
  const [currencies, setCurrencies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [receiptUrl, setReceiptUrl] = useState('');
  
  const [formData, setFormData] = useState({
    category_id: '',
    amount: '',
    currency: 'USD',
    expense_date: new Date().toISOString().split('T')[0],
    paid_by: 'personal',
    description: '',
  });

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    
    loadCategories();
    loadCurrencies();
  }, [user]);

  const loadCategories = async () => {
    try {
      const response = await api.categories.list();
      if (response.data.success) {
        // Filter only active categories
        const activeCategories = response.data.data.filter((cat: any) => cat.is_active);
        setCategories(activeCategories);
      }
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  };

  const loadCurrencies = async () => {
    try {
      const response = await api.countries.currencies();
      if (response.data.success) {
        setCurrencies(response.data.data);
      }
    } catch (err) {
      console.error('Failed to load currencies:', err);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      
      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        return;
      }
      
      // Validate file type
      const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        setError('Only images (PNG, JPG, GIF) and PDF files are allowed');
        return;
      }
      
      setSelectedFile(file);
      setError('');
    }
  };

  const uploadReceipt = async () => {
    if (!selectedFile) return;
    
    setUploading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('folder', 'receipts');
      
      const response = await api.upload.file(formData);
      
      if (response.data.success) {
        setReceiptUrl(response.data.data.url);
        setError('');
      } else {
        setError(response.data.message || 'Upload failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to upload receipt');
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent, submit: boolean = false) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Validate form
      if (!formData.category_id || !formData.amount || !formData.currency || !formData.expense_date) {
        setError('Please fill in all required fields');
        setLoading(false);
        return;
      }
      
      // Create expense data
      const expenseData = {
        ...formData,
        category_id: formData.category_id, // Keep as string (UUID)
        amount: parseFloat(formData.amount),
        receipt_url: receiptUrl || null,
      };
      
      // Create expense
      const response = await api.expenses.create(expenseData);
      
      if (response.data.success) {
        const expenseId = response.data.data.id;
        
        // If submit flag is true, submit for approval
        if (submit) {
          await api.expenses.submit(expenseId);
          alert('Expense submitted for approval successfully!');
        } else {
          alert('Expense saved as draft successfully!');
        }
        
        router.push('/expenses');
      } else {
        setError(response.data.message || 'Failed to create expense');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create expense');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  if (!user) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      {/* Navigation Bar */}
      <div className="mb-6 flex items-center justify-between bg-white p-4 rounded-lg shadow">
        <div className="flex space-x-4">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            ← Dashboard
          </button>
          <span className="text-gray-400">|</span>
          <button
            onClick={() => router.push('/expenses')}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            My Expenses
          </button>
          <span className="text-gray-400">|</span>
          <span className="text-gray-900 font-semibold">
            Create New
          </span>
        </div>
      </div>
      
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Create New Expense</h1>
        <button
          onClick={() => router.push('/expenses')}
          className="text-blue-600 hover:text-blue-800"
        >
          ← Back to Expenses
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={(e) => handleSubmit(e, false)} className="bg-white shadow-md rounded-lg p-6">
        {/* Category */}
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="category_id">
            Category <span className="text-red-500">*</span>
          </label>
          <select
            id="category_id"
            name="category_id"
            value={formData.category_id}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Select a category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        {/* Amount and Currency */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="amount">
              Amount <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              id="amount"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              step="0.01"
              min="0.01"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0.00"
              required
            />
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="currency">
              Currency <span className="text-red-500">*</span>
            </label>
            <select
              id="currency"
              name="currency"
              value={formData.currency}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              {currencies.map((currency) => (
                <option key={currency.code} value={currency.code}>
                  {currency.code} ({currency.symbol})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Expense Date and Paid By */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="expense_date">
              Expense Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              id="expense_date"
              name="expense_date"
              value={formData.expense_date}
              onChange={handleChange}
              max={new Date().toISOString().split('T')[0]}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="paid_by">
              Paid By <span className="text-red-500">*</span>
            </label>
            <select
              id="paid_by"
              name="paid_by"
              value={formData.paid_by}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="personal">Personal</option>
              <option value="company">Company</option>
            </select>
          </div>
        </div>

        {/* Description */}
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter expense description..."
          />
        </div>

        {/* Receipt Upload */}
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Receipt (Optional)
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
            {!receiptUrl ? (
              <>
                <input
                  type="file"
                  accept="image/*,.pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="fileUpload"
                />
                <label
                  htmlFor="fileUpload"
                  className="flex flex-col items-center justify-center cursor-pointer"
                >
                  <svg className="w-12 h-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span className="text-sm text-gray-600">
                    {selectedFile ? selectedFile.name : 'Click to upload or drag and drop'}
                  </span>
                  <span className="text-xs text-gray-500 mt-1">PNG, JPG, GIF, PDF (max 5MB)</span>
                </label>
                {selectedFile && (
                  <button
                    type="button"
                    onClick={uploadReceipt}
                    disabled={uploading}
                    className="mt-3 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {uploading ? 'Uploading...' : 'Upload Receipt'}
                  </button>
                )}
              </>
            ) : (
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <svg className="w-8 h-8 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm text-gray-700">Receipt uploaded successfully</span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setReceiptUrl('');
                    setSelectedFile(null);
                  }}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-gray-600 text-white py-3 px-4 rounded-md hover:bg-gray-700 disabled:bg-gray-400 font-medium"
          >
            {loading ? 'Saving...' : 'Save as Draft'}
          </button>
          
          <button
            type="button"
            onClick={(e) => handleSubmit(e, true)}
            disabled={loading}
            className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 font-medium"
          >
            {loading ? 'Submitting...' : 'Submit for Approval'}
          </button>
        </div>
      </form>
    </div>
  );
}
