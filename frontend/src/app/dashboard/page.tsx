'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Navbar } from '@/components/navbar';
import { api } from '@/lib/api';
import { Expense } from '@/types';
import { toast } from 'sonner';
import { 
  Clock, 
  CheckCircle2, 
  XCircle, 
  FileText,
  PlusCircle,
  Receipt,
  DollarSign,
  Calendar,
  Loader2
} from 'lucide-react';
import Link from 'next/link';

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

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const stats = {
    total: expenses.length,
    approved: expenses.filter((e) => e.status === 'approved').length,
    pending: expenses.filter((e) => e.status === 'submitted').length,
    rejected: expenses.filter((e) => e.status === 'rejected').length,
    draft: expenses.filter((e) => e.status === 'draft').length,
    totalAmount: expenses
      .filter((e) => e.status === 'approved')
      .reduce((sum, e) => sum + e.amount, 0),
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, {user?.name}! 👋
          </h1>
          <p className="text-muted-foreground">
            Here's an overview of your expense activity
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card className="border-l-4 border-l-primary">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription>Total Expenses</CardDescription>
                <FileText className="h-5 w-5 text-muted-foreground" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.total}</div>
              <p className="text-xs text-muted-foreground mt-1">All time</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-green-500">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription>Approved</CardDescription>
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">{stats.approved}</div>
              <p className="text-xs text-muted-foreground mt-1">
                ${stats.totalAmount.toFixed(2)} total
              </p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-yellow-500">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription>Pending</CardDescription>
                <Clock className="h-5 w-5 text-yellow-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600">{stats.pending}</div>
              <p className="text-xs text-muted-foreground mt-1">Awaiting approval</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-red-500">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription>Rejected</CardDescription>
                <XCircle className="h-5 w-5 text-red-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">{stats.rejected}</div>
              <p className="text-xs text-muted-foreground mt-1">Review needed</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          <Button
            onClick={() => router.push('/expenses/new')}
            size="lg"
            className="h-auto py-6 justify-start"
          >
            <PlusCircle className="h-5 w-5 mr-3" />
            <div className="text-left">
              <div className="font-semibold">Create New Expense</div>
              <div className="text-xs opacity-90">Add a new expense entry</div>
            </div>
          </Button>

          <Button
            onClick={() => router.push('/expenses')}
            variant="outline"
            size="lg"
            className="h-auto py-6 justify-start"
          >
            <Receipt className="h-5 w-5 mr-3" />
            <div className="text-left">
              <div className="font-semibold">View All Expenses</div>
              <div className="text-xs text-muted-foreground">Manage your expenses</div>
            </div>
          </Button>
        </div>

        {/* Recent Expenses */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Expenses</CardTitle>
                <CardDescription className="mt-1">
                  Your latest expense submissions
                </CardDescription>
              </div>
              <Link href="/expenses">
                <Button variant="outline" size="sm">
                  View All
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {expenses.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-lg font-medium mb-2">No expenses yet</p>
                <p className="text-muted-foreground mb-6">
                  Create your first expense to get started!
                </p>
                <Button onClick={() => router.push('/expenses/new')}>
                  <PlusCircle className="h-4 w-4 mr-2" />
                  Create First Expense
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {expenses.slice(0, 5).map((expense) => (
                  <div
                    key={expense.id}
                    onClick={() => router.push(`/expenses/${expense.id}`)}
                    className="flex items-center justify-between p-4 border rounded-lg hover:border-primary hover:bg-accent cursor-pointer transition-colors"
                  >
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <DollarSign className="h-5 w-5 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">
                          {expense.description || 'No description'}
                        </p>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Calendar className="h-3 w-3" />
                          {expense.expense_date}
                          {expense.categories?.name && (
                            <>
                              <span>•</span>
                              <span>{expense.categories.name}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <div className="text-right">
                        <p className="font-bold">
                          {expense.currency} {expense.amount.toFixed(2)}
                        </p>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          expense.status === 'approved'
                            ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                            : expense.status === 'rejected'
                            ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                            : expense.status === 'submitted'
                            ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                            : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400'
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
