'use client';

import React, { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { dashboardService } from '@/services/dashboard';
import { DashboardMetrics, UpcomingWeddingSummary } from '@/types';
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
  const [dashboardMetrics, setDashboardMetrics] = useState<DashboardMetrics | null>(null);
  const [upcomingWeddings, setUpcomingWeddings] = useState<UpcomingWeddingSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        // FIX: Use correct service methods
        const [metrics, weddings] = await Promise.all([
          dashboardService.getDashboardMetrics(),
          dashboardService.getUpcomingWeddings(30)
        ]);
        setDashboardMetrics(metrics);
        setUpcomingWeddings(weddings);
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
                  <p className="text-2xl font-bold text-gray-900">{dashboardMetrics?.couples.total || 0}</p>
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
                  <p className="text-2xl font-bold text-gray-900">{dashboardMetrics?.ceremonies.upcoming_30_days || 0}</p>
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
                  <p className="text-sm font-medium text-gray-600">Legal Forms Urgent</p>
                  <p className="text-2xl font-bold text-gray-900">{dashboardMetrics?.legal_forms.urgent_attention || 0}</p>
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
                    {formatCurrency(dashboardMetrics?.revenue.monthly || 0)}
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
              {upcomingWeddings?.ceremonies?.length ? (
                <div className="space-y-4">
                  {upcomingWeddings.ceremonies.slice(0, 5).map((wedding) => (
                    <div key={wedding.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">{wedding.couple.names}</p>
                        <p className="text-sm text-gray-600">
                          {formatDate(wedding.ceremony.date)} {wedding.ceremony.time && `at ${wedding.ceremony.time}`}
                        </p>
                        {wedding.ceremony.venue && (
                          <p className="text-sm text-gray-500">{wedding.ceremony.venue}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(wedding.ceremony.status)}`}>
                          {wedding.ceremony.status}
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                          {wedding.ceremony.days_until > 0 ? `${wedding.ceremony.days_until} days` : 'Today'}
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

          {/* Revenue Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Revenue Summary</CardTitle>
              <CardDescription>Financial overview</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Revenue</span>
                  <span className="font-semibold">{formatCurrency(dashboardMetrics?.revenue.total || 0)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">This Month</span>
                  <span className="font-semibold">{formatCurrency(dashboardMetrics?.revenue.monthly || 0)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Outstanding</span>
                  <span className="font-semibold text-yellow-600">
                    {formatCurrency(dashboardMetrics?.revenue.outstanding_amount || 0)}
                    {dashboardMetrics?.revenue.outstanding_count ? ` (${dashboardMetrics.revenue.outstanding_count})` : ''}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Overdue</span>
                  <span className="font-semibold text-red-600">
                    {formatCurrency(dashboardMetrics?.revenue.overdue_amount || 0)}
                    {dashboardMetrics?.revenue.overdue_count ? ` (${dashboardMetrics.revenue.overdue_count})` : ''}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Summary Stats */}
        {upcomingWeddings?.summary && (
          <Card>
            <CardHeader>
              <CardTitle>Wedding Summary</CardTitle>
              <CardDescription>Ceremony schedule overview</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{upcomingWeddings.summary.this_week}</p>
                  <p className="text-sm text-gray-600">This Week</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{upcomingWeddings.summary.next_week}</p>
                  <p className="text-sm text-gray-600">Next Week</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{upcomingWeddings.summary.this_month}</p>
                  <p className="text-sm text-gray-600">This Month</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{formatCurrency(upcomingWeddings.summary.total_revenue)}</p>
                  <p className="text-sm text-gray-600">Expected Revenue</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
} 