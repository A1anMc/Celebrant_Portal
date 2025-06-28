'use client';

import { useState } from 'react';
import DashboardLayout from '../../src/components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/Card';
import { Input } from '../../src/components/ui/Input';
import { Button } from '../../src/components/ui/Button';
import { User, Mail, Phone, Building2, Globe, DollarSign, Save } from 'lucide-react';

export default function SettingsPage() {
  const [loading, setLoading] = useState(false);

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-fade-in bg-gradient-to-br from-secondary via-background to-accent-light -m-6 lg:-m-8 min-h-screen p-6 lg:p-8">
        <div className="space-y-1">
          <h1 className="text-4xl font-serif font-bold text-primary-dark">Settings</h1>
          <p className="text-lg text-foreground/70">Manage your profile and business preferences</p>
        </div>
        
        <div className="space-y-6">
          {/* Profile Settings */}
          <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="bg-primary/10 p-2 rounded-full">
                  <User className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-xl font-serif text-primary-dark">Profile Information</CardTitle>
                  <CardDescription>Update your personal details and contact information</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground/70 mb-2">Full Name</label>
                <Input type="text" placeholder="Your full name" className="border-border focus:border-primary" />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/70 mb-2">Email</label>
                <Input type="email" placeholder="your@email.com" className="border-border focus:border-primary" />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/70 mb-2">Phone</label>
                <Input type="tel" placeholder="Your phone number" className="border-border focus:border-primary" />
              </div>
            </CardContent>
          </Card>

          {/* Business Settings */}
          <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="bg-success/10 p-2 rounded-full">
                  <Building2 className="h-5 w-5 text-success" />
                </div>
                <div>
                  <CardTitle className="text-xl font-serif text-primary-dark">Business Details</CardTitle>
                  <CardDescription>Manage your business information and legal details</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground/70 mb-2">Business Name</label>
                <Input type="text" placeholder="Your business name" className="border-border focus:border-primary" />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/70 mb-2">ABN</label>
                <Input type="text" placeholder="Australian Business Number" className="border-border focus:border-primary" />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/70 mb-2">Business Address</label>
                <Input type="text" placeholder="Your business address" className="border-border focus:border-primary" />
              </div>
            </CardContent>
          </Card>

          {/* Preferences */}
          <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="bg-accent/20 p-2 rounded-full">
                  <Globe className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-xl font-serif text-primary-dark">Preferences</CardTitle>
                  <CardDescription>Configure your regional and display preferences</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground/70 mb-2">Timezone</label>
                <select className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                  <option>Australia/Melbourne</option>
                  <option>Australia/Sydney</option>
                  <option>Australia/Brisbane</option>
                  <option>Australia/Adelaide</option>
                  <option>Australia/Perth</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/70 mb-2">Currency</label>
                <select className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                  <option>AUD</option>
                  <option>USD</option>
                  <option>EUR</option>
                  <option>GBP</option>
                </select>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end pt-4">
            <Button 
              onClick={() => {}} 
              disabled={loading}
              size="lg"
              className="bg-primary hover:bg-primary-dark text-white shadow-soft hover:shadow-soft-lg transition-all duration-200"
            >
              <Save className="mr-2 h-4 w-4" />
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
} 