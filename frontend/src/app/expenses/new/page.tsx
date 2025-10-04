"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ThemeToggle } from '@/components/theme-toggle';
import { toast } from 'sonner';
import { ArrowLeft, Upload, X, FileText, DollarSign, Calendar, Tag } from 'lucide-react';

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
          toast.success('Expense submitted for approval successfully!');
        } else {
          toast.success('Expense saved as draft successfully!');
        }
        
        router.push('/expenses');
      } else {
        setError(response.data.message || 'Failed to create expense');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create expense');
      toast.error(err.response?.data?.message || 'Failed to create expense');
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
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b bg-card sticky top-0 z-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push('/expenses')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back</span>
              </Button>
              <div className="h-6 w-px bg-border" />
              <h1 className="text-xl font-semibold">Create Expense</h1>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 sm:px-6 lg:px-8 py-6 max-w-5xl">
        <Card className="h-full">
          <CardContent className="p-6">
            {error && (
              <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg mb-4">
                {error}
              </div>
            )}

            <form onSubmit={(e) => handleSubmit(e, false)} className="space-y-6">
              {/* Row 1: Category, Amount, Currency */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="category_id" className="flex items-center space-x-1">
                    <Tag className="h-4 w-4" />
                    <span>Category</span>
                    <span className="text-destructive">*</span>
                  </Label>
                  <select
                    id="category_id"
                    name="category_id"
                    value={formData.category_id}
                    onChange={handleChange}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 [&>option]:bg-background [&>option]:text-foreground [&>option:disabled]:text-muted-foreground"
                    required
                  >
                    <option value="" disabled className="bg-background text-muted-foreground">Select category</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id} className="bg-background text-foreground">
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="amount" className="flex items-center space-x-1">
                    <DollarSign className="h-4 w-4" />
                    <span>Amount</span>
                    <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    type="number"
                    id="amount"
                    name="amount"
                    value={formData.amount}
                    onChange={handleChange}
                    step="0.01"
                    min="0.01"
                    placeholder="0.00"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="currency">Currency <span className="text-destructive">*</span></Label>
                  <select
                    id="currency"
                    name="currency"
                    value={formData.currency}
                    onChange={handleChange}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 [&>option]:bg-background [&>option]:text-foreground"
                    required
                  >
                    {currencies.map((currency) => (
                      <option key={currency.code} value={currency.code} className="bg-background text-foreground">
                        {currency.code} ({currency.symbol})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Row 2: Date and Paid By */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="expense_date" className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                    <span>Expense Date</span>
                    <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    type="date"
                    id="expense_date"
                    name="expense_date"
                    value={formData.expense_date}
                    onChange={handleChange}
                    max={new Date().toISOString().split('T')[0]}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="paid_by">Paid By <span className="text-destructive">*</span></Label>
                  <select
                    id="paid_by"
                    name="paid_by"
                    value={formData.paid_by}
                    onChange={handleChange}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 [&>option]:bg-background [&>option]:text-foreground"
                    required
                  >
                    <option value="personal" className="bg-background text-foreground">Personal</option>
                    <option value="company" className="bg-background text-foreground">Company</option>
                  </select>
                </div>
              </div>

              {/* Row 3: Description */}
              <div className="space-y-2">
                <Label htmlFor="description" className="flex items-center space-x-1">
                  <FileText className="h-4 w-4" />
                  <span>Description</span>
                </Label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={3}
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 resize-none"
                  placeholder="Enter expense description..."
                />
              </div>

              {/* Row 4: Receipt Upload */}
              <div className="space-y-2">
                <Label className="flex items-center space-x-1">
                  <Upload className="h-4 w-4" />
                  <span>Receipt (Optional)</span>
                </Label>
                <div className="border-2 border-dashed border-border rounded-lg p-4 bg-muted/20">
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
                        className="flex flex-col items-center justify-center cursor-pointer py-2"
                      >
                        <Upload className="h-8 w-8 text-muted-foreground mb-2" />
                        <span className="text-sm text-foreground font-medium">
                          {selectedFile ? selectedFile.name : 'Click to upload'}
                        </span>
                        <span className="text-xs text-muted-foreground mt-1">PNG, JPG, GIF, PDF (max 5MB)</span>
                      </label>
                      {selectedFile && (
                        <Button
                          type="button"
                          onClick={uploadReceipt}
                          disabled={uploading}
                          className="mt-3 w-full"
                          variant="outline"
                        >
                          {uploading ? 'Uploading...' : 'Upload Receipt'}
                        </Button>
                      )}
                    </>
                  ) : (
                    <div className="flex items-center justify-between py-2">
                      <div className="flex items-center space-x-2">
                        <div className="h-8 w-8 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                          <Upload className="h-4 w-4 text-green-600 dark:text-green-400" />
                        </div>
                        <span className="text-sm font-medium">Receipt uploaded</span>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setReceiptUrl('');
                          setSelectedFile(null);
                        }}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-2">
                <Button
                  type="submit"
                  disabled={loading}
                  variant="outline"
                  className="flex-1"
                  size="lg"
                >
                  {loading ? 'Saving...' : 'Save as Draft'}
                </Button>
                
                <Button
                  type="button"
                  onClick={(e) => handleSubmit(e, true)}
                  disabled={loading}
                  className="flex-1"
                  size="lg"
                >
                  {loading ? 'Submitting...' : 'Submit for Approval'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
