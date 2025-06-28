'use client';

import DashboardLayout from '../../src/components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/Card';
import { DollarSign, Clock, CheckCircle, AlertCircle, Receipt, TrendingUp } from 'lucide-react';

export default function InvoicesPage() {
  return (
    <DashboardLayout>
      <div className="space-y-8 animate-fade-in">
        <div className="space-y-1">
          <h1 className="text-4xl font-serif font-bold text-primary-dark flex items-center">
            <Receipt className="h-8 w-8 text-primary mr-3" />
            Invoices & Billing
          </h1>
          <p className="text-lg text-foreground/70">Manage your financial transactions and payments</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="shadow-soft hover:shadow-soft-lg transition-all duration-200 border-border/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground/70">Total Revenue</p>
                  <p className="text-3xl font-serif font-bold text-primary-dark">$0.00</p>
                  <p className="text-sm text-success flex items-center mt-1">
                    <TrendingUp className="h-3 w-3 mr-1" />
                    This month
                  </p>
                </div>
                <div className="bg-success/10 p-3 rounded-full">
                  <DollarSign className="h-6 w-6 text-success" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-soft hover:shadow-soft-lg transition-all duration-200 border-border/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground/70">Pending</p>
                  <p className="text-3xl font-serif font-bold text-primary-dark">0</p>
                  <p className="text-sm text-foreground/60 mt-1">Awaiting payment</p>
                </div>
                <div className="bg-warning/10 p-3 rounded-full">
                  <Clock className="h-6 w-6 text-warning" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-soft hover:shadow-soft-lg transition-all duration-200 border-border/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground/70">Paid</p>
                  <p className="text-3xl font-serif font-bold text-primary-dark">0</p>
                  <p className="text-sm text-foreground/60 mt-1">Last 30 days</p>
                </div>
                <div className="bg-primary/10 p-3 rounded-full">
                  <CheckCircle className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-soft hover:shadow-soft-lg transition-all duration-200 border-border/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground/70">Overdue</p>
                  <p className="text-3xl font-serif font-bold text-primary-dark">0</p>
                  <p className="text-sm text-foreground/60 mt-1">Needs attention</p>
                </div>
                <div className="bg-destructive/10 p-3 rounded-full">
                  <AlertCircle className="h-6 w-6 text-destructive" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="shadow-soft border-border/50">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="bg-accent/20 p-2 rounded-full">
                <Receipt className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="text-xl font-serif text-primary-dark">Coming Soon</CardTitle>
                <CardDescription>Professional invoicing system</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-foreground/70 mb-4">
              The invoicing system is coming soon. You'll be able to:
            </p>
            <ul className="list-disc list-inside space-y-2 text-foreground/60">
              <li>Create and send professional invoices</li>
              <li>Track payments and send reminders</li>
              <li>Generate financial reports</li>
              <li>Set up automated payment processing</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
} 