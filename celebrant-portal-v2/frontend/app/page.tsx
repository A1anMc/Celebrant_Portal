'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../src/contexts/AuthContext';
import { Button } from '../src/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../src/components/ui/Card';
import { 
  Users, 
  Calendar, 
  FileText, 
  DollarSign, 
  Shield, 
  Heart,
  ArrowRight
} from 'lucide-react';

export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const handleGetStarted = () => {
    if (user) {
      router.push('/dashboard');
    } else {
      router.push('/login');
    }
  };

  const handleSignIn = () => {
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-secondary via-background to-accent-light">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary via-background to-accent-light">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-accent/10"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-serif font-bold text-primary-dark mb-6">
              Melbourne Celebrant Portal
            </h1>
            <p className="text-xl md:text-2xl text-foreground/80 mb-8 max-w-3xl mx-auto">
              The complete business management platform designed specifically for Australian marriage celebrants
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button 
                size="lg"
                onClick={handleGetStarted}
                className="bg-primary hover:bg-primary-dark text-white px-8 py-3 text-lg font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
              >
                {user ? 'Go to Dashboard' : 'Join Beta - Free Access'}
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              
              {!user && (
                <Button 
                  variant="outline"
                  size="lg"
                  onClick={handleSignIn}
                  className="border-primary text-primary hover:bg-primary hover:text-white px-8 py-3 text-lg font-semibold rounded-lg transition-all duration-200"
                >
                  Sign In
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-background/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-serif font-bold text-primary-dark mb-4">
              Everything You Need to Run Your Celebrant Business
            </h2>
            <p className="text-lg text-foreground/70 max-w-2xl mx-auto">
              From initial inquiry to final invoice, manage every aspect of your celebrant practice with professional tools designed for your success.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  <Users className="h-8 w-8 text-primary" />
                  <h3 className="text-xl font-serif font-semibold text-primary-dark ml-3">Couple Management</h3>
                </div>
                <p className="text-foreground/70 leading-relaxed">
                  Organize all your client relationships and ceremony details in one beautiful interface.
                </p>
              </CardContent>
            </Card>

            <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  <Calendar className="h-8 w-8 text-primary" />
                  <h3 className="text-xl font-serif font-semibold text-primary-dark ml-3">Ceremony Planning</h3>
                </div>
                <p className="text-foreground/70 leading-relaxed">
                  Plan perfect ceremonies with templates, timelines, and venue management tools.
                </p>
              </CardContent>
            </Card>

            <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  <FileText className="h-8 w-8 text-primary" />
                  <h3 className="text-xl font-serif font-semibold text-primary-dark ml-3">Legal Compliance</h3>
                </div>
                <p className="text-foreground/70 leading-relaxed">
                  Never miss a NOIM deadline with automated tracking and compliance reminders.
                </p>
              </CardContent>
            </Card>

            <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  <DollarSign className="h-8 w-8 text-primary" />
                  <h3 className="text-xl font-serif font-semibold text-primary-dark ml-3">Financial Management</h3>
                </div>
                <p className="text-foreground/70 leading-relaxed">
                  Professional invoicing, payment tracking, and business analytics at your fingertips.
                </p>
              </CardContent>
            </Card>

            <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  <Shield className="h-8 w-8 text-primary" />
                  <h3 className="text-xl font-serif font-semibold text-primary-dark ml-3">Secure & Reliable</h3>
                </div>
                <p className="text-foreground/70 leading-relaxed">
                  Bank-level security with automatic backups and Australian data hosting.
                </p>
              </CardContent>
            </Card>

            <Card className="shadow-soft hover:shadow-soft-lg transition-shadow duration-200">
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  <Heart className="h-8 w-8 text-primary" />
                  <h3 className="text-xl font-serif font-semibold text-primary-dark ml-3">Made for Celebrants</h3>
                </div>
                <p className="text-foreground/70 leading-relaxed">
                  Built specifically for Australian marriage celebrants by celebrants who understand your needs.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-20 bg-gradient-to-r from-primary/10 to-accent/10">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-serif font-bold text-primary-dark mb-6">
            Ready to Transform Your Celebrant Business?
          </h2>
          <p className="text-lg text-foreground/70 mb-8 max-w-2xl mx-auto">
            Join hundreds of Australian celebrants who have streamlined their business operations and increased their professional success with our platform.
          </p>
          <Button 
            size="lg"
            onClick={handleGetStarted}
            className="bg-primary hover:bg-primary-dark text-white px-10 py-4 text-xl font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
          >
            {user ? 'Go to Dashboard' : 'Join Beta Waitlist'}
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-serif font-bold text-primary-dark mb-4">Melbourne Celebrant Portal</h3>
            <p className="text-foreground/60 mb-6">Professional marriage celebrant management platform</p>
            <div className="flex justify-center space-x-6 text-sm text-foreground/50">
              <span>© 2024 Melbourne Celebrant Portal</span>
              <span>•</span>
              <span>Made in Australia</span>
              <span>•</span>
              <span>For Australian Celebrants</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
} 