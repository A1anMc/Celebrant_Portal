'use client';

import React, { useState } from 'react';
import DashboardLayout from '../../src/components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/Card';
import { Button } from '../../src/components/ui/Button';
import { 
  BarChart3, 
  TrendingUp, 
  Calendar, 
  DollarSign,
  Users,
  FileText,
  Download,
  Filter,
  Eye,
  Heart
} from 'lucide-react';

export default function ReportsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState('Last 6 Months');

  const mockData = [
    { period: 'Jan', ceremonies: 8, revenue: 12000 },
    { period: 'Feb', ceremonies: 12, revenue: 18000 },
    { period: 'Mar', ceremonies: 15, revenue: 24000 },
    { period: 'Apr', ceremonies: 10, revenue: 16500 },
    { period: 'May', ceremonies: 18, revenue: 30600 },
    { period: 'Jun', ceremonies: 22, revenue: 39600 }
  ];

  const totalRevenue = mockData.reduce((sum, data) => sum + data.revenue, 0);
  const totalCeremonies = mockData.reduce((sum, data) => sum + data.ceremonies, 0);

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-fade-in">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="space-y-1">
            <h1 className="text-4xl font-serif font-bold text-primary-dark">Reports & Analytics</h1>
            <p className="text-lg text-foreground/70">Track your business performance and growth</p>
          </div>
          <Button size="lg" className="bg-primary hover:bg-primary-dark text-white shadow-soft hover:shadow-soft-lg">
            <Download className="mr-2 h-4 w-4" />
            Export Report
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground/70">Total Revenue</p>
                  <p className="text-3xl font-serif font-bold text-primary-dark">
                    ${totalRevenue.toLocaleString()}
                  </p>
                  <p className="text-sm text-success flex items-center mt-1">
                    <TrendingUp className="h-3 w-3 mr-1" />
                    +25% growth
                  </p>
                </div>
                <div className="bg-primary/10 p-3 rounded-full">
                  <DollarSign className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground/70">Total Ceremonies</p>
                  <p className="text-3xl font-serif font-bold text-primary-dark">{totalCeremonies}</p>
                  <p className="text-sm text-foreground/60 mt-1">6 months period</p>
                </div>
                <div className="bg-success/10 p-3 rounded-full">
                  <Heart className="h-6 w-6 text-success" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground/70">Total Couples</p>
                  <p className="text-3xl font-serif font-bold text-primary-dark">{totalCeremonies}</p>
                  <p className="text-sm text-foreground/60 mt-1">Happy clients</p>
                </div>
                <div className="bg-accent/20 p-3 rounded-full">
                  <Users className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground/70">Avg. Booking Value</p>
                  <p className="text-3xl font-serif font-bold text-primary-dark">
                    ${Math.round(totalRevenue / totalCeremonies).toLocaleString()}
                  </p>
                  <p className="text-sm text-foreground/60 mt-1">Per ceremony</p>
                </div>
                <div className="bg-warning/10 p-3 rounded-full">
                  <BarChart3 className="h-6 w-6 text-warning" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="shadow-soft">
            <CardHeader>
              <CardTitle className="text-xl font-serif text-primary-dark">Revenue Trend</CardTitle>
              <CardDescription>Monthly revenue over the selected period</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-end justify-between space-x-2 p-4">
                {mockData.map((data, index) => (
                  <div key={data.period} className="flex flex-col items-center flex-1">
                    <div 
                      className="w-full bg-primary rounded-t-lg transition-all duration-500 hover:bg-primary-dark"
                      style={{ 
                        height: `${(data.revenue / Math.max(...mockData.map(d => d.revenue))) * 200}px`
                      }}
                    ></div>
                    <p className="text-xs text-foreground/60 mt-2 text-center">{data.period}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-soft">
            <CardHeader>
              <CardTitle className="text-xl font-serif text-primary-dark">Ceremony Volume</CardTitle>
              <CardDescription>Number of ceremonies per month</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-end justify-between space-x-2 p-4">
                {mockData.map((data, index) => (
                  <div key={data.period} className="flex flex-col items-center flex-1">
                    <div 
                      className="w-full bg-success rounded-t-lg transition-all duration-500 hover:bg-success/80"
                      style={{ 
                        height: `${(data.ceremonies / Math.max(...mockData.map(d => d.ceremonies))) * 200}px`
                      }}
                    ></div>
                    <p className="text-xs text-foreground/60 mt-2 text-center">{data.period}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="shadow-soft">
          <CardHeader>
            <CardTitle className="text-xl font-serif text-primary-dark">Detailed Reports</CardTitle>
            <CardDescription>Generate and download comprehensive business reports</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors">
                <div className="flex items-center space-x-3 mb-3">
                  <FileText className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold text-foreground">Financial Summary</h3>
                </div>
                <p className="text-sm text-foreground/60 mb-4">Complete financial overview with revenue, expenses, and profit analysis.</p>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="h-4 w-4 mr-1" />
                    Preview
                  </Button>
                  <Button size="sm" className="bg-primary hover:bg-primary-dark text-white">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors">
                <div className="flex items-center space-x-3 mb-3">
                  <Calendar className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold text-foreground">Ceremony Report</h3>
                </div>
                <p className="text-sm text-foreground/60 mb-4">Detailed breakdown of all ceremonies, including dates, venues, and status.</p>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="h-4 w-4 mr-1" />
                    Preview
                  </Button>
                  <Button size="sm" className="bg-primary hover:bg-primary-dark text-white">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors">
                <div className="flex items-center space-x-3 mb-3">
                  <Users className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold text-foreground">Client Analysis</h3>
                </div>
                <p className="text-sm text-foreground/60 mb-4">Comprehensive client data including demographics and booking patterns.</p>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="h-4 w-4 mr-1" />
                    Preview
                  </Button>
                  <Button size="sm" className="bg-primary hover:bg-primary-dark text-white">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
} 