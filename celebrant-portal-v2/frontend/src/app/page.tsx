'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Heart, Calendar, FileText, DollarSign, Users, Shield } from 'lucide-react';

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-secondary via-background to-accent-light">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const features = [
    {
      icon: <Users className="h-8 w-8 text-primary" />,
      title: "Couple Management",
      description: "Organize all your client relationships and ceremony details in one beautiful interface."
    },
    {
      icon: <Calendar className="h-8 w-8 text-primary" />,
      title: "Ceremony Planning",
      description: "Plan perfect ceremonies with templates, timelines, and venue management tools."
    },
    {
      icon: <FileText className="h-8 w-8 text-primary" />,
      title: "Legal Compliance",
      description: "Never miss a NOIM deadline with automated tracking and compliance reminders."
    },
    {
      icon: <DollarSign className="h-8 w-8 text-primary" />,
      title: "Financial Management",
      description: "Professional invoicing, payment tracking, and business analytics at your fingertips."
    },
    {
      icon: <Shield className="h-8 w-8 text-primary" />,
      title: "Secure & Reliable",
      description: "Bank-level security with automatic backups and Australian data hosting."
    },
    {
      icon: <Heart className="h-8 w-8 text-primary" />,
      title: "Made for Celebrants",
      description: "Built specifically for Australian marriage celebrants by celebrants who understand your needs."
    }
  ];

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
                onClick={() => router.push('/beta')}
                className="bg-primary hover:bg-primary-dark text-white px-8 py-3 text-lg font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
              >
                Join Beta - Free Access
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => router.push('/login')}
                className="border-primary text-primary hover:bg-primary hover:text-white px-8 py-3 text-lg font-semibold rounded-lg transition-all duration-200"
              >
                Sign In
              </Button>
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
            {features.map((feature, index) => (
              <Card key={index} className="p-6 bg-card border-border hover:shadow-lg transition-shadow duration-200">
                <div className="flex items-center mb-4">
                  {feature.icon}
                  <h3 className="text-xl font-serif font-semibold text-primary-dark ml-3">
                    {feature.title}
                  </h3>
                </div>
                <p className="text-foreground/70 leading-relaxed">
                  {feature.description}
                </p>
              </Card>
            ))}
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
            onClick={() => router.push('/beta')}
            className="bg-primary hover:bg-primary-dark text-white px-10 py-4 text-xl font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
          >
            Join Beta Waitlist
          </Button>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-serif font-bold text-primary-dark mb-4">
              Melbourne Celebrant Portal
            </h3>
            <p className="text-foreground/60 mb-6">
              Professional marriage celebrant management platform
            </p>
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
