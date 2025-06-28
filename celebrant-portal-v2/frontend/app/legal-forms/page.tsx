'use client';

import DashboardLayout from '../../src/components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/Card';
import { FileText, AlertTriangle, CheckCircle, Scale, Clock, Archive } from 'lucide-react';

export default function LegalFormsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-8 animate-fade-in">
        <div className="space-y-1">
          <h1 className="text-4xl font-serif font-bold text-primary-dark flex items-center">
            <Scale className="h-8 w-8 text-primary mr-3" />
            Legal Forms
          </h1>
          <p className="text-lg text-foreground/70">Manage legal documentation and compliance</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className="shadow-soft hover:shadow-soft-lg transition-all duration-200 border-border/50">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="bg-primary/10 p-2 rounded-full">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-lg font-serif text-primary-dark">Required Forms</CardTitle>
                  <CardDescription>Essential legal documents</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-foreground/70">View and manage required legal documents for upcoming ceremonies.</p>
            </CardContent>
          </Card>

          <Card className="shadow-soft hover:shadow-soft-lg transition-all duration-200 border-border/50">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="bg-warning/10 p-2 rounded-full">
                  <Clock className="h-5 w-5 text-warning" />
                </div>
                <div>
                  <CardTitle className="text-lg font-serif text-primary-dark">Pending Review</CardTitle>
                  <CardDescription>Awaiting attention</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-foreground/70">Forms that need your attention or approval.</p>
            </CardContent>
          </Card>

          <Card className="shadow-soft hover:shadow-soft-lg transition-all duration-200 border-border/50">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="bg-success/10 p-2 rounded-full">
                  <CheckCircle className="h-5 w-5 text-success" />
                </div>
                <div>
                  <CardTitle className="text-lg font-serif text-primary-dark">Completed</CardTitle>
                  <CardDescription>Successfully processed</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-foreground/70">Successfully processed and approved forms.</p>
            </CardContent>
          </Card>
        </div>

        <Card className="shadow-soft border-border/50">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="bg-accent/20 p-2 rounded-full">
                <Archive className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="text-xl font-serif text-primary-dark">Coming Soon</CardTitle>
                <CardDescription>Enhanced legal forms management system</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-foreground/70 mb-4">
              The full legal forms management system is coming soon. You'll be able to:
            </p>
            <ul className="list-disc list-inside space-y-2 text-foreground/60">
              <li>Track and manage all legal documentation</li>
              <li>Set up automated reminders for form submissions</li>
              <li>Generate compliance reports</li>
              <li>Securely store and access archived forms</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
} 