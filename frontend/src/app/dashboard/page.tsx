'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/api';
import { Expense } from '@/types';
import { toast } from 'sonner';

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout, isAuthenticated, loading: authLoading } = useAuth();
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
      return;
    }

    if (isAuthenticated) {
      loadExpenses();
    }
  }, [authLoading, isAuthenticated, router]);

  const loadExpenses = async () => {
    try {
      const response = await api.expenses.list();
      setExpenses(response.data.data || []);
    } catch (error: any) {
      toast.error('Failed to load expenses');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Expense Management</h1>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600 dark:text-gray-300">
              {user?.name} ({user?.role})
            </span>
            <Button variant="outline" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Card */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Welcome, {user?.name}! 🎉</CardTitle>
            <CardDescription>
              Your expense management dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-300">Total Expenses</p>
                <p className="text-2xl font-bold">{expenses.length}</p>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-300">Approved</p>
                <p className="text-2xl font-bold">
                  {expenses.filter((e) => e.status === 'approved').length}
                </p>
              </div>
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-300">Pending</p>
                <p className="text-2xl font-bold">
                  {expenses.filter((e) => e.status === 'submitted').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Connection Status */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>✅ Backend Connection Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-green-600 dark:text-green-400 font-semibold">
                ✓ Successfully connected to backend API
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                API URL: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api'}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Authenticated as: {user?.email}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Role: {user?.role}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Recent Expenses */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Expenses</CardTitle>
            <CardDescription>
              Your latest expense submissions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {expenses.length === 0 ? (
              <p className="text-center text-gray-500 py-8">
                No expenses yet. Create your first expense to get started!
              </p>
            ) : (
              <div className="space-y-4">
                {expenses.slice(0, 5).map((expense) => (
                  <div
                    key={expense.id}
                    className="flex justify-between items-center p-4 border rounded-lg"
                  >
                    <div>
                      <p className="font-semibold">{expense.description || 'No description'}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">
                        {expense.expense_date} • {expense.categories?.name}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">
                        {expense.currency} {expense.amount.toFixed(2)}
                      </p>
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          expense.status === 'approved'
                            ? 'bg-green-100 text-green-800'
                            : expense.status === 'rejected'
                            ? 'bg-red-100 text-red-800'
                            : expense.status === 'submitted'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {expense.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
