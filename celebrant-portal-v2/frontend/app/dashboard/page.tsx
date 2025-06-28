'use client';

import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../src/components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardStats } from '../../src/components/ui/Card';
import { Button } from '../../src/components/ui/Button';
import { dashboardService } from '../../src/services/dashboard';
import { DashboardMetrics, UpcomingWeddingSummary } from '../../src/types';
import { formatCurrency, formatDate, getDaysUntil, getStatusColor } from '../../src/lib/utils';
import { 
  Users, 
  Calendar, 
  FileText, 
  DollarSign, 
  AlertTriangle,
  Plus,
  Eye,
  TrendingUp,
  Clock,
  Heart
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
        <div className="space-y-8 animate-fade-in">
          <div className="flex justify-between items-center">
            <div className="space-y-2">
              <div className="h-8 bg-muted rounded w-48 animate-pulse"></div>
              <div className="h-4 bg-muted rounded w-72 animate-pulse"></div>
            </div>
            <div className="h-10 bg-muted rounded w-32 animate-pulse"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-muted rounded w-1/2"></div>
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
        <div className="text-center py-12 animate-fade-in">
          <div className="bg-destructive/10 border border-destructive/20 text-destructive px-6 py-4 rounded-xl max-w-md mx-auto">
            <AlertTriangle className="h-6 w-6 mx-auto mb-2" />
            <p className="font-medium">Error Loading Dashboard</p>
            <p className="text-sm mt-1">{error}</p>
            <Button 
              variant="outline" 
              size="sm" 
              className="mt-3"
              onClick={() => window.location.reload()}
            >
              Try Again
            </Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-fade-in">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="space-y-1">
            <h1 className="text-4xl font-serif font-bold text-primary-dark">Dashboard</h1>
            <p className="text-lg text-foreground/70">Welcome back! Here's what's happening with your ceremonies.</p>
          </div>
          <Link href="/couples/new">
            <Button 
              size="lg" 
              className="bg-primary hover:bg-primary-dark text-white shadow-soft hover:shadow-soft-lg transition-all duration-200"
            >
              <Plus className="mr-2 h-5 w-5" />
              New Couple
            </Button>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <CardStats
            value={dashboardMetrics?.couples.total || 0}
            label="Total Couples"
            icon={<Users className="h-6 w-6 text-primary" />}
            trend="up"
            trendValue="+3 this month"
            className="animate-slide-up"
          />

          <CardStats
            value={dashboardMetrics?.ceremonies.upcoming_30_days || 0}
            label="Upcoming Ceremonies"
            icon={<Calendar className="h-6 w-6 text-success" />}
            trend="neutral"
            trendValue="Next 30 days"
            className="animate-slide-up"
            style={{ animationDelay: '100ms' }}
          />

          <CardStats
            value={dashboardMetrics?.legal_forms.urgent_attention || 0}
            label="Legal Forms Urgent"
            icon={<FileText className="h-6 w-6 text-warning" />}
            trend={dashboardMetrics?.legal_forms.urgent_attention ? "down" : "neutral"}
            trendValue="Require attention"
            className="animate-slide-up"
            style={{ animationDelay: '200ms' }}
          />

          <CardStats
            value={formatCurrency(dashboardMetrics?.revenue.monthly || 0)}
            label="Monthly Revenue"
            icon={<DollarSign className="h-6 w-6 text-primary" />}
            trend="up"
            trendValue="+12% from last month"
            className="animate-slide-up"
            style={{ animationDelay: '300ms' }}
          />
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upcoming Weddings */}
          <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Heart className="h-5 w-5 text-primary" />
                  <CardTitle className="text-xl">Upcoming Weddings</CardTitle>
                </div>
                <Calendar className="h-5 w-5 text-foreground/40" />
              </div>
              <CardDescription>Your next ceremonies to celebrate love</CardDescription>
            </CardHeader>
            <CardContent>
              {upcomingWeddings?.ceremonies?.length ? (
                <div className="space-y-4">
                  {upcomingWeddings.ceremonies.slice(0, 5).map((wedding, index) => (
                    <div 
                      key={wedding.id} 
                      className="flex items-center justify-between p-4 bg-gradient-to-r from-muted/30 to-accent/20 rounded-xl border border-border/50 hover:shadow-soft transition-all duration-200"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <div className="flex-1">
                        <p className="font-serif font-semibold text-primary-dark">{wedding.couple.names}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Clock className="h-4 w-4 text-foreground/50" />
                          <p className="text-sm text-foreground/70">
                            {formatDate(wedding.ceremony.date)} {wedding.ceremony.time && `at ${wedding.ceremony.time}`}
                          </p>
                        </div>
                        {wedding.ceremony.venue && (
                          <p className="text-sm text-foreground/60 mt-1">{wedding.ceremony.venue}</p>
                        )}
                      </div>
                      <div className="text-right ml-4">
                        <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(wedding.ceremony.status)}`}>
                          {wedding.ceremony.status}
                        </div>
                        <p className="text-sm text-foreground/60 mt-1 font-medium">
                          {wedding.ceremony.days_until > 0 ? `${wedding.ceremony.days_until} days` : 'Today'}
                        </p>
                      </div>
                    </div>
                  ))}
                  <Link href="/couples">
                    <Button variant="outline" size="sm" className="w-full mt-4 border-primary/30 hover:bg-primary/5">
                      <Eye className="mr-2 h-4 w-4" />
                      View All Couples
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="bg-muted/30 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <Calendar className="h-8 w-8 text-foreground/40" />
                  </div>
                  <p className="text-foreground/60 font-medium">No upcoming weddings</p>
                  <p className="text-sm text-foreground/50 mt-1">Start by adding your first couple</p>
                  <Link href="/couples/new">
                    <Button variant="outline" size="sm" className="mt-4">
                      <Plus className="mr-2 h-4 w-4" />
                      Add New Couple
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions & Legal Forms Status */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
              <CardHeader>
                <CardTitle className="text-xl flex items-center">
                  <TrendingUp className="h-5 w-5 text-primary mr-2" />
                  Quick Actions
                </CardTitle>
                <CardDescription>Common tasks to keep your business running smoothly</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-3">
                  <Link href="/couples/new">
                    <Button variant="outline" className="w-full justify-start h-12 hover:bg-primary/5">
                      <Plus className="mr-3 h-4 w-4" />
                      Add New Couple
                    </Button>
                  </Link>
                  <Link href="/templates">
                    <Button variant="outline" className="w-full justify-start h-12 hover:bg-primary/5">
                      <FileText className="mr-3 h-4 w-4" />
                      Manage Templates
                    </Button>
                  </Link>
                  <Link href="/legal-forms">
                    <Button variant="outline" className="w-full justify-start h-12 hover:bg-primary/5">
                      <AlertTriangle className="mr-3 h-4 w-4" />
                      Check Legal Forms
                    </Button>
                  </Link>
                  <Link href="/invoices">
                    <Button variant="outline" className="w-full justify-start h-12 hover:bg-primary/5">
                      <DollarSign className="mr-3 h-4 w-4" />
                      Create Invoice
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>

            {/* Legal Forms Alert */}
            {dashboardMetrics?.legal_forms.urgent_attention && dashboardMetrics.legal_forms.urgent_attention > 0 && (
              <Card className="border-warning/30 bg-warning/5 shadow-soft">
                <CardHeader>
                  <CardTitle className="text-warning flex items-center">
                    <AlertTriangle className="h-5 w-5 mr-2" />
                    Legal Forms Alert
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-foreground/70 mb-4">
                    You have {dashboardMetrics.legal_forms.urgent_attention} legal forms requiring immediate attention.
                  </p>
                  <Link href="/legal-forms">
                    <Button variant="warning" size="sm" className="w-full">
                      Review Legal Forms
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
} 