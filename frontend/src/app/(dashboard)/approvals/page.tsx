'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { CheckCircle2, XCircle, Clock, TrendingUp, FileText } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

interface Approval {
  id: string;
  expense_id: string;
  rule_id: string;
  approver_user_id: string;
  status: 'pending' | 'approved' | 'rejected';
  comments?: string;
  approved_at?: string;
  order_index: number;
  expense?: {
    id: string;
    amount: number;
    currency: string;
    expense_date: string;
    description: string;
    status: string;
    receipt_url?: string;
    paid_by?: string;
    converted_amount?: number;
    company_currency?: string;
    user?: {
      name: string;
      email: string;
    };
    category?: {
      name: string;
    };
  };
  approver?: {
    id: string;
    name: string;
    email: string;
  };
  rule?: {
    name: string;
    approval_percentage: number;
    is_sequential: boolean;
  };
}

interface ApprovalStats {
  total_pending: number;
  total_approved: number;
  total_rejected: number;
  total_approvals: number;
}

export default function ApprovalsPage() {
  const router = useRouter();
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [stats, setStats] = useState<ApprovalStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedApproval, setSelectedApproval] = useState<Approval | null>(null);
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState('pending');

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      if (!token) {
        router.push('/login');
        return;
      }

      // Build query params
      const params = new URLSearchParams();
      if (activeTab !== 'all') {
        params.append('status', activeTab);
      }

      // Fetch approvals and stats
      const [approvalsRes, statsRes] = await Promise.all([
        fetch(`${API_URL}/api/approvals?${params}`, {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
        fetch(`${API_URL}/api/approvals/stats`, {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
      ]);

      const approvalsData = await approvalsRes.json();
      const statsData = await statsRes.json();

      if (approvalsData.success) {
        setApprovals(approvalsData.data || []);
      } else {
        toast.error(approvalsData.message);
      }

      if (statsData.success) {
        setStats(statsData.data);
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to load approvals');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async () => {
    if (!selectedApproval || !actionType) return;

    if (actionType === 'reject' && !comments.trim()) {
      toast.error('Comments are required when rejecting');
      return;
    }

    try {
      setSubmitting(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(
        `${API_URL}/api/approvals/${selectedApproval.id}/${actionType}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ comments }),
        }
      );

      const data = await response.json();

      if (data.success) {
        toast.success(data.message || `Expense ${actionType}d successfully`);
        setSelectedApproval(null);
        setActionType(null);
        setComments('');
        loadData();
      } else {
        toast.error(data.message || `Failed to ${actionType} expense`);
      }
    } catch (error: any) {
      toast.error(error.message || `Failed to ${actionType} expense`);
    } finally {
      setSubmitting(false);
    }
  };

  const openActionDialog = (approval: Approval, type: 'approve' | 'reject') => {
    setSelectedApproval(approval);
    setActionType(type);
    setComments('');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Approvals Dashboard</h1>
        <p className="text-muted-foreground">
          Review and manage expense approval requests
        </p>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Pending
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-3xl font-bold text-yellow-600">{stats.total_pending}</span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4" />
                Approved
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-3xl font-bold text-green-600">{stats.total_approved}</span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <XCircle className="h-4 w-4" />
                Rejected
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-3xl font-bold text-red-600">{stats.total_rejected}</span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Total
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-3xl font-bold text-blue-600">{stats.total_approvals}</span>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs for filtering */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full md:w-auto grid-cols-4">
          <TabsTrigger value="pending">
            Pending {stats && `(${stats.total_pending})`}
          </TabsTrigger>
          <TabsTrigger value="approved">Approved</TabsTrigger>
          <TabsTrigger value="rejected">Rejected</TabsTrigger>
          <TabsTrigger value="all">All</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-6">
          {loading ? (
            <Card>
              <CardContent className="pt-6 text-center py-12">
                <div className="flex flex-col items-center gap-2">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                  <p className="text-muted-foreground">Loading approvals...</p>
                </div>
              </CardContent>
            </Card>
          ) : approvals.length === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground text-lg">No approvals found</p>
                <p className="text-sm text-muted-foreground mt-2">
                  {activeTab === 'pending'
                    ? 'You have no pending approval requests at the moment.'
                    : `No ${activeTab} approvals to display.`}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {approvals.map((approval) => (
                <Card key={approval.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <CardTitle className="text-xl flex items-center gap-2 flex-wrap">
                          <span className="font-bold">
                            {approval.expense?.currency} {approval.expense?.amount?.toLocaleString()}
                          </span>
                          {approval.expense?.converted_amount && (
                            <span className="text-base text-muted-foreground font-normal">
                              ≈ {approval.expense.company_currency}{' '}
                              {approval.expense.converted_amount.toLocaleString()}
                            </span>
                          )}
                        </CardTitle>
                        <CardDescription className="mt-2 flex flex-col gap-1">
                          <span>
                            Submitted by <strong>{approval.expense?.user?.name}</strong>
                          </span>
                          <span className="text-xs">
                            {approval.expense?.expense_date &&
                              formatDate(approval.expense.expense_date)}
                          </span>
                        </CardDescription>
                      </div>
                      <Badge
                        className={`${getStatusColor(approval.status)} border whitespace-nowrap`}
                      >
                        {approval.status.toUpperCase()}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4 text-sm">
                      <div>
                        <span className="font-semibold">Category:</span>{' '}
                        <span className="text-muted-foreground">
                          {approval.expense?.category?.name || 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="font-semibold">Paid by:</span>{' '}
                        <span className="text-muted-foreground capitalize">
                          {approval.expense?.paid_by || 'N/A'}
                        </span>
                      </div>
                      <div className="md:col-span-2">
                        <span className="font-semibold">Description:</span>{' '}
                        <span className="text-muted-foreground">
                          {approval.expense?.description || 'No description provided'}
                        </span>
                      </div>
                      <div>
                        <span className="font-semibold">Approval Rule:</span>{' '}
                        <span className="text-muted-foreground">{approval.rule?.name}</span>
                      </div>
                      <div>
                        <span className="font-semibold">Email:</span>{' '}
                        <span className="text-muted-foreground">
                          {approval.expense?.user?.email}
                        </span>
                      </div>
                      {approval.comments && (
                        <div className="md:col-span-2 p-3 bg-muted rounded-md">
                          <span className="font-semibold">Comments:</span>{' '}
                          <span className="text-muted-foreground">{approval.comments}</span>
                        </div>
                      )}
                    </div>

                    {approval.status === 'pending' && (
                      <div className="flex gap-2 flex-wrap">
                        <Button
                          onClick={() => openActionDialog(approval, 'approve')}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <CheckCircle2 className="mr-2 h-4 w-4" />
                          Approve
                        </Button>
                        <Button
                          onClick={() => openActionDialog(approval, 'reject')}
                          variant="destructive"
                        >
                          <XCircle className="mr-2 h-4 w-4" />
                          Reject
                        </Button>
                        {approval.expense?.receipt_url && (
                          <Button
                            variant="outline"
                            onClick={() => window.open(approval.expense?.receipt_url, '_blank')}
                          >
                            <FileText className="mr-2 h-4 w-4" />
                            View Receipt
                          </Button>
                        )}
                      </div>
                    )}

                    {approval.status !== 'pending' && approval.approved_at && (
                      <div className="text-sm text-muted-foreground mt-2">
                        {approval.status === 'approved' ? 'Approved' : 'Rejected'} on{' '}
                        {formatDate(approval.approved_at)}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Action Dialog */}
      <Dialog open={!!actionType} onOpenChange={() => setActionType(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {actionType === 'approve' ? '✅ Approve' : '❌ Reject'} Expense
            </DialogTitle>
            <DialogDescription>
              {selectedApproval && (
                <div className="mt-2 space-y-1">
                  <div className="font-semibold text-base text-foreground">
                    {selectedApproval.expense?.currency}{' '}
                    {selectedApproval.expense?.amount?.toLocaleString()}
                  </div>
                  <div>
                    Submitted by {selectedApproval.expense?.user?.name} (
                    {selectedApproval.expense?.user?.email})
                  </div>
                  <div className="text-xs">
                    {selectedApproval.expense?.description || 'No description'}
                  </div>
                </div>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <label className="text-sm font-medium mb-2 block">
              Comments {actionType === 'reject' && <span className="text-red-500">*</span>}
            </label>
            <Textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder={
                actionType === 'approve'
                  ? 'Optional: Add comments about this approval...'
                  : 'Required: Please provide a reason for rejection...'
              }
              rows={4}
              className="resize-none"
            />
            {actionType === 'reject' && (
              <p className="text-xs text-muted-foreground mt-2">
                Comments are required when rejecting an expense to provide feedback to the
                submitter.
              </p>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setActionType(null)} disabled={submitting}>
              Cancel
            </Button>
            <Button
              onClick={handleAction}
              disabled={submitting || (actionType === 'reject' && !comments.trim())}
              className={
                actionType === 'approve'
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-red-600 hover:bg-red-700'
              }
            >
              {submitting
                ? 'Processing...'
                : actionType === 'approve'
                ? '✅ Approve Expense'
                : '❌ Reject Expense'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
