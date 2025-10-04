"use client";

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export default function ViewExpensePage() {
  const router = useRouter();
  const params = useParams();
  const expenseId = params?.id as string;
  const { user } = useAuth();
  
  const [expense, setExpense] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    
    loadExpense();
  }, [user, expenseId]);

  const loadExpense = async () => {
    try {
      const response = await api.expenses.get(expenseId);
      if (response.data.success) {
        setExpense(response.data.data);
      } else {
        setError(response.data.message || 'Failed to load expense');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load expense');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: any = {
      draft: 'bg-gray-200 text-gray-800',
      submitted: 'bg-yellow-200 text-yellow-800',
      approved: 'bg-green-200 text-green-800',
      rejected: 'bg-red-200 text-red-800',
    };
    
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${badges[status] || 'bg-gray-200 text-gray-800'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (!user || loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>;
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
        <button
          onClick={() => router.push('/expenses')}
          className="mt-4 text-blue-600 hover:text-blue-800"
        >
          ← Back to Expenses
        </button>
      </div>
    );
  }

  if (!expense) {
    return <div className="flex justify-center items-center min-h-screen">Expense not found</div>;
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
            Expense Details
          </span>
        </div>
      </div>
      
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Expense Details</h1>
        <button
          onClick={() => router.push('/expenses')}
          className="text-blue-600 hover:text-blue-800"
        >
          ← Back to List
        </button>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        {/* Header with Status */}
        <div className="bg-gray-50 px-6 py-4 border-b flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {expense.category?.name || 'Uncategorized'}
            </h2>
            <p className="text-sm text-gray-500">
              Expense ID: {expense.id}
            </p>
          </div>
          {getStatusBadge(expense.status)}
        </div>

        {/* Expense Details */}
        <div className="px-6 py-6 space-y-6">
          {/* Amount */}
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Amount</label>
            <p className="text-3xl font-bold text-gray-900">
              {expense.currency} {parseFloat(expense.amount).toFixed(2)}
            </p>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Expense Date</label>
              <p className="text-lg text-gray-900">
                {new Date(expense.expense_date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Paid By</label>
              <p className="text-lg text-gray-900 capitalize">
                <span className={expense.paid_by === 'company' ? 'text-blue-600 font-medium' : ''}>
                  {expense.paid_by}
                </span>
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Currency</label>
              <p className="text-lg text-gray-900">{expense.currency}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Status</label>
              <p className="text-lg text-gray-900 capitalize">{expense.status}</p>
            </div>

            {expense.submitted_at && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Submitted At</label>
                  <p className="text-lg text-gray-900">
                    {new Date(expense.submitted_at).toLocaleString()}
                  </p>
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Created At</label>
              <p className="text-lg text-gray-900">
                {new Date(expense.created_at).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Description */}
          {expense.description && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Description</label>
              <p className="text-gray-900 whitespace-pre-wrap">{expense.description}</p>
            </div>
          )}

          {/* Receipt */}
          {expense.receipt_url && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-2">Receipt</label>
              <a
                href={expense.receipt_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                View Receipt
              </a>
            </div>
          )}

          {/* Submitted By */}
          {expense.user && (
            <div className="pt-4 border-t">
              <label className="block text-sm font-medium text-gray-500 mb-1">Submitted By</label>
              <p className="text-gray-900">
                {expense.user.name} ({expense.user.email})
              </p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="bg-gray-50 px-6 py-4 border-t flex gap-3">
          {expense.status === 'draft' && (
            <>
              <button
                onClick={() => router.push(`/expenses/${expense.id}/edit`)}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 font-medium"
              >
                Edit Expense
              </button>
              <button
                onClick={async () => {
                  if (confirm('Submit this expense for approval?')) {
                    try {
                      await api.expenses.submit(expense.id);
                      alert('Expense submitted for approval');
                      loadExpense(); // Reload to show updated status
                    } catch (err: any) {
                      alert(err.response?.data?.message || 'Failed to submit');
                    }
                  }
                }}
                className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 font-medium"
              >
                Submit for Approval
              </button>
            </>
          )}
          
          {expense.status !== 'draft' && (
            <button
              onClick={() => router.push('/expenses')}
              className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 font-medium"
            >
              Back to List
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
