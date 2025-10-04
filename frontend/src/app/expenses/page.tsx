"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Navbar } from '@/components/navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import {
  FileText,
  Filter,
  Search,
  Eye,
  Edit,
  Trash2,
  Send,
  Paperclip,
  PlusCircle,
  Calendar,
  DollarSign,
  Tag
} from 'lucide-react';

export default function ExpensesPage() {
  const router = useRouter();
  const { user } = useAuth();
  
  const [expenses, setExpenses] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  
  const [filters, setFilters] = useState({
    status: '',
    category_id: '',
  });

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    
    loadExpenses();
    loadStats();
  }, [user]);

  const loadExpenses = async () => {
    try {
      setLoading(true);
      const params: any = {};
      
      if (filters.status) params.status = filters.status;
      if (filters.category_id) params.category_id = filters.category_id;
      
      const response = await api.expenses.list(params);
      
      if (response.data.success) {
        setExpenses(response.data.data);
      } else {
        setError(response.data.message || 'Failed to load expenses');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load expenses');
      toast.error('Failed to load expenses');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.expenses.stats();
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this expense?')) return;
    
    try {
      const response = await api.expenses.delete(id);
      
      if (response.data.success) {
        toast.success('Expense deleted successfully');
        loadExpenses();
        loadStats();
      } else {
        toast.error(response.data.message || 'Failed to delete expense');
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to delete expense');
    }
  };

  const handleSubmit = async (id: string) => {
    if (!confirm('Submit this expense for approval?')) return;
    
    try {
      const response = await api.expenses.submit(id);
      
      if (response.data.success) {
        toast.success('Expense submitted for approval');
        loadExpenses();
        loadStats();
      } else {
        toast.error(response.data.message || 'Failed to submit expense');
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to submit expense');
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
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${badges[status] || 'bg-gray-100 text-gray-700'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const filteredExpenses = expenses.filter(expense =>
    expense.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    expense.category?.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center space-y-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold mb-2">My Expenses</h1>
            <p className="text-muted-foreground text-lg">
              Track and manage all your expenses
            </p>
          </div>
          <Button
            onClick={() => router.push('/expenses/new')}
            size="lg"
            className="flex items-center space-x-2"
          >
            <PlusCircle className="h-5 w-5" />
            <span>Create Expense</span>
          </Button>
        </div>

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardDescription>Total</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stats.total_expenses}</div>
              </CardContent>
            </Card>
            <Card className="border-l-4 border-l-gray-500 hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardDescription>Draft</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-gray-600">{stats.draft_count}</div>
              </CardContent>
            </Card>
            <Card className="border-l-4 border-l-yellow-500 hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardDescription>Submitted</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-yellow-600">{stats.submitted_count}</div>
              </CardContent>
            </Card>
            <Card className="border-l-4 border-l-green-500 hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardDescription>Approved</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">{stats.approved_count}</div>
              </CardContent>
            </Card>
          </div>
        )}

        {error && (
          <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Search and Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Filter className="h-5 w-5" />
              <span>Search & Filter</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <Label htmlFor="search">Search</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search"
                    type="text"
                    placeholder="Search by description or category..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 h-11"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="status">Status</Label>
                <select
                  id="status"
                  value={filters.status}
                  onChange={(e) => {
                    setFilters({ ...filters, status: e.target.value });
                    setTimeout(loadExpenses, 100);
                  }}
                  className="flex h-11 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="">All Statuses</option>
                  <option value="draft">Draft</option>
                  <option value="submitted">Submitted</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Expenses List */}
        {loading ? (
          <Card>
            <CardContent className="py-12">
              <div className="flex flex-col items-center space-y-4">
                <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
                <p className="text-muted-foreground">Loading expenses...</p>
              </div>
            </CardContent>
          </Card>
        ) : filteredExpenses.length === 0 ? (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <div className="h-20 w-20 rounded-full bg-muted mx-auto mb-4 flex items-center justify-center">
                  <FileText className="h-10 w-10 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-medium mb-2">No expenses found</h3>
                <p className="text-muted-foreground mb-6">
                  {searchTerm ? 'Try adjusting your search' : 'Create your first expense to get started'}
                </p>
                {!searchTerm && (
                  <Button onClick={() => router.push('/expenses/new')} size="lg">
                    <PlusCircle className="h-5 w-5 mr-2" />
                    Create Expense
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {filteredExpenses.map((expense) => (
              <Card
                key={expense.id}
                className="hover:shadow-lg transition-all border-2 hover:border-primary/50"
                // onClick={() => router.push(`/expenses/${expense.id}`)}
              >
                <CardContent className="p-4 sm:p-6">
                  <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                    {/* Main Info */}
                    <div className="flex items-start space-x-4 flex-1 min-w-0">
                      <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <DollarSign className="h-6 w-6 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <h3 className="font-semibold text-lg truncate">
                            {expense.description || 'No description'}
                          </h3>
                          <div className="flex-shrink-0 lg:hidden">
                            {getStatusBadge(expense.status)}
                          </div>
                        </div>
                        <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                          <div className="flex items-center">
                            <Calendar className="h-4 w-4 mr-1" />
                            {new Date(expense.expense_date).toLocaleDateString()}
                          </div>
                          {expense.category?.name && (
                            <div className="flex items-center">
                              <Tag className="h-4 w-4 mr-1" />
                              {expense.category.name}
                            </div>
                          )}
                          <div className="flex items-center">
                            <span className={`capitalize ${expense.paid_by === 'company' ? 'text-primary font-medium' : ''}`}>
                              {expense.paid_by}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Amount and Actions */}
                    <div className="flex items-center justify-between lg:justify-end gap-4 lg:gap-6">
                      <div className="text-right">
                        <div className="text-2xl font-bold">
                          {expense.currency} {parseFloat(expense.amount).toFixed(2)}
                        </div>
                      </div>
                      
                      <div className="hidden lg:block">
                        {getStatusBadge(expense.status)}
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                        {expense.receipt_url && (
                          <Button
                            variant="outline"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation();
                              window.open(expense.receipt_url, '_blank');
                            }}
                            title="View Receipt"
                          >
                            <Paperclip className="h-4 w-4" />
                          </Button>
                        )}
                        
                        {expense.status === 'draft' && (
                          <>
                            <Button
                              variant="outline"
                              size="icon"
                              onClick={(e) => {
                                e.stopPropagation();
                                router.push(`/expenses/${expense.id}/edit`);
                              }}
                              title="Edit"
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="icon"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleSubmit(expense.id);
                              }}
                              title="Submit"
                              className="text-green-600 hover:text-green-700"
                            >
                              <Send className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="icon"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(expense.id);
                              }}
                              title="Delete"
                              className="text-destructive hover:text-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                        
                        {expense.status !== 'draft' && (
                          <Button
                            className='cursor-pointer'
                            variant="outline"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation();
                              router.push(`/expenses/${expense.id}`);
                            }}
                            title="View Details"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
