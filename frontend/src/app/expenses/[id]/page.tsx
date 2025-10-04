"use client";

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Navbar } from '@/components/navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import {
  ArrowLeft,
  Calendar,
  DollarSign,
  FileText,
  User,
  Tag,
  ExternalLink,
  Edit,
  Send,
  CheckCircle2,
  XCircle,
  Clock,
  Image as ImageIcon
} from 'lucide-react';

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
      toast.error('Failed to load expense');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!confirm('Submit this expense for approval?')) return;
    
    try {
      const response = await api.expenses.submit(expense.id);
      if (response.data.success) {
        toast.success('Expense submitted for approval');
        loadExpense();
      } else {
        toast.error(response.data.message || 'Failed to submit expense');
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to submit expense');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle2 className="h-6 w-6 text-green-600" />;
      case 'rejected':
        return <XCircle className="h-6 w-6 text-red-600" />;
      case 'submitted':
        return <Clock className="h-6 w-6 text-yellow-600" />;
      default:
        return <FileText className="h-6 w-6 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: any = {
      draft: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
      submitted: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
      approved: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      rejected: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    };
    
    return (
      <div className="flex items-center space-x-2">
        {getStatusIcon(status)}
        <span className={`px-4 py-2 rounded-full text-sm font-semibold ${badges[status] || 'bg-gray-100 text-gray-700'}`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>
    );
  };

  if (!user || loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="flex justify-center items-center min-h-[60vh]">
          <div className="flex flex-col items-center space-y-4">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            <p className="text-muted-foreground">Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-4 py-8 max-w-3xl">
          <Card className="border-destructive">
            <CardContent className="pt-6">
              <div className="text-center">
                <XCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Error Loading Expense</h3>
                <p className="text-muted-foreground mb-4">{error}</p>
                <Button onClick={() => router.push('/expenses')} variant="outline">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Expenses
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!expense) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-4 py-8 max-w-3xl">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Expense not found</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 max-w-4xl">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => router.push('/expenses')}
          className="mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Expenses
        </Button>

        {/* Header Card */}
        <Card className="mb-6 border-2">
          <CardHeader>
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center space-x-2 text-muted-foreground mb-2">
                  <Tag className="h-4 w-4" />
                  <span className="text-sm">{expense.category?.name || 'Uncategorized'}</span>
                </div>
                <CardTitle className="text-3xl mb-2">
                  {expense.description || 'Expense Details'}
                </CardTitle>
                <CardDescription className="text-base">
                  ID: {expense.id}
                </CardDescription>
              </div>
              {getStatusBadge(expense.status)}
            </div>
          </CardHeader>
        </Card>

        {/* Amount Card */}
        <Card className="mb-6 bg-gradient-to-br from-primary/5 to-primary/10 border-2">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <DollarSign className="h-8 w-8 text-primary" />
              </div>
              <p className="text-sm text-muted-foreground mb-2">Total Amount</p>
              <p className="text-5xl font-bold text-primary">
                {expense.currency} {parseFloat(expense.amount).toFixed(2)}
              </p>
              <p className="text-sm text-muted-foreground mt-2 capitalize">
                Paid by {expense.paid_by}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-2 text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <CardDescription>Expense Date</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-xl font-semibold">
                {new Date(expense.expense_date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-2 text-muted-foreground">
                <DollarSign className="h-4 w-4" />
                <CardDescription>Currency</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-xl font-semibold">{expense.currency}</p>
            </CardContent>
          </Card>

          {expense.submitted_at && (
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  <CardDescription>Submitted At</CardDescription>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-lg font-semibold">
                  {new Date(expense.submitted_at).toLocaleString()}
                </p>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-2 text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <CardDescription>Created At</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-lg font-semibold">
                {new Date(expense.created_at).toLocaleString()}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Description */}
        {expense.description && (
          <Card className="mb-6">
            <CardHeader>
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-muted-foreground" />
                <CardTitle className="text-lg">Description</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-foreground whitespace-pre-wrap leading-relaxed">
                {expense.description}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Receipt */}
        {expense.receipt_url && (
          <Card className="mb-6">
            <CardHeader>
              <div className="flex items-center space-x-2">
                <ImageIcon className="h-5 w-5 text-muted-foreground" />
                <CardTitle className="text-lg">Receipt</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => window.open(expense.receipt_url, '_blank')}
                size="lg"
                variant="outline"
                className="w-full sm:w-auto"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                View Receipt
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Submitter Info */}
        {expense.user && (
          <Card className="mb-6">
            <CardHeader>
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5 text-muted-foreground" />
                <CardTitle className="text-lg">Submitted By</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-lg font-medium">{expense.user.name}</p>
              <p className="text-muted-foreground">{expense.user.email}</p>
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col sm:flex-row gap-3">
              {expense.status === 'draft' && (
                <>
                  <Button
                    onClick={() => router.push(`/expenses/${expense.id}/edit`)}
                    size="lg"
                    variant="outline"
                    className="flex-1"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit Expense
                  </Button>
                  <Button
                    onClick={handleSubmit}
                    size="lg"
                    className="flex-1"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Submit for Approval
                  </Button>
                </>
              )}
              
              {expense.status !== 'draft' && (
                <Button
                  onClick={() => router.push('/expenses')}
                  size="lg"
                  variant="outline"
                  className="w-full"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to List
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
