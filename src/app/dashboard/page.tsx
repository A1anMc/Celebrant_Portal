'use client';

import React, { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { dashboardService } from '@/services/dashboard';
import { DashboardData } from '@/types';
import { formatCurrency, formatDate, getDaysUntil, getStatusColor } from '@/lib/utils';
import { 
  Users, 
  Calendar, 
  FileText, 
  DollarSign, 
  AlertTriangle,
  Plus,
  Eye
} from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const data = await dashboardService.getDashboardData();
        setDashboardData(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
            {error}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const stats = dashboardData?.stats;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600">Welcome back! Here's what's happening with your ceremonies.</p>
          </div>
          <Link href="/couples/new">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Couple
            </Button>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Couples</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.total_couples || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Calendar className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Upcoming Ceremonies</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.upcoming_ceremonies || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <FileText className="h-6 w-6 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Pending NOIM Forms</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.pending_noim_forms || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <DollarSign className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(stats?.monthly_revenue || 0)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upcoming Weddings */}
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Weddings</CardTitle>
              <CardDescription>Your next ceremonies</CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData?.upcoming_weddings?.length ? (
                <div className="space-y-4">
                  {dashboardData.upcoming_weddings.slice(0, 5).map((wedding) => (
                    <div key={wedding.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">{wedding.couple_names}</p>
                        <p className="text-sm text-gray-600">
                          {formatDate(wedding.ceremony_date)} {wedding.ceremony_time && `at ${wedding.ceremony_time}`}
                        </p>
                        {wedding.venue && (
                          <p className="text-sm text-gray-500">{wedding.venue}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(wedding.status)}`}>
                          {wedding.status}
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                          {wedding.days_until > 0 ? `${wedding.days_until} days` : 'Today'}
                        </p>
                      </div>
                    </div>
                  ))}
                  <Link href="/couples">
                    <Button variant="outline" size="sm" className="w-full">
                      <Eye className="mr-2 h-4 w-4" />
                      View All Couples
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="text-center py-6">
                  <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No upcoming weddings</p>
                  <Link href="/couples/new">
                    <Button variant="outline" size="sm" className="mt-2">
                      Add Your First Couple
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Enquiries */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Enquiries</CardTitle>
              <CardDescription>Latest couple enquiries</CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData?.recent_enquiries?.length ? (
                <div className="space-y-4">
                  {dashboardData.recent_enquiries.slice(0, 5).map((couple) => (
                    <div key={couple.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">
                          {couple.partner1.first_name} {couple.partner1.last_name} & {couple.partner2.first_name} {couple.partner2.last_name}
                        </p>
                        <p className="text-sm text-gray-600">
                          {couple.ceremony_type} • {couple.ceremony_date ? formatDate(couple.ceremony_date) : 'Date TBD'}
                        </p>
                      </div>
                      <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(couple.status)}`}>
                        {couple.status}
                      </div>
                    </div>
                  ))}
                  <Link href="/couples?status=enquiry">
                    <Button variant="outline" size="sm" className="w-full">
                      <Eye className="mr-2 h-4 w-4" />
                      View All Enquiries
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="text-center py-6">
                  <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No recent enquiries</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Pending Tasks */}
        {(dashboardData?.pending_tasks?.noim_forms?.length || dashboardData?.pending_tasks?.overdue_invoices?.length) && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertTriangle className="mr-2 h-5 w-5 text-yellow-600" />
                Pending Tasks
              </CardTitle>
              <CardDescription>Items requiring your attention</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardData.pending_tasks.noim_forms?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">NOIM Forms Due</h4>
                    <div className="space-y-2">
                      {dashboardData.pending_tasks.noim_forms.slice(0, 3).map((form) => (
                        <div key={form.id} className="flex items-center justify-between p-2 bg-yellow-50 rounded">
                          <span className="text-sm">{form.form_name}</span>
                          <span className="text-xs text-yellow-700">
                            {form.expiry_date && getDaysUntil(form.expiry_date) > 0 
                              ? `${getDaysUntil(form.expiry_date)} days left`
                              : 'Overdue'
                            }
                          </span>
                        </div>
                      ))}
                    </div>
                    <Link href="/legal-forms?status=pending">
                      <Button variant="outline" size="sm" className="mt-2">
                        View All NOIM Forms
                      </Button>
                    </Link>
                  </div>
                )}

                {dashboardData.pending_tasks.overdue_invoices?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Overdue Invoices</h4>
                    <div className="space-y-2">
                      {dashboardData.pending_tasks.overdue_invoices.slice(0, 3).map((invoice) => (
                        <div key={invoice.id} className="flex items-center justify-between p-2 bg-red-50 rounded">
                          <span className="text-sm">{invoice.invoice_number}</span>
                          <span className="text-xs text-red-700">
                            {formatCurrency(invoice.total_amount)}
                          </span>
                        </div>
                      ))}
                    </div>
                    <Link href="/invoices?status=overdue">
                      <Button variant="outline" size="sm" className="mt-2">
                        View All Overdue Invoices
                      </Button>
                    </Link>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
} 