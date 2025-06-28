'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '../src/components/ui/Button';
import { Heart, Home, Users, FileText } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-secondary via-background to-accent-light py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        <div className="space-y-6">
          <div className="flex justify-center">
            <div className="bg-primary/10 p-4 rounded-full shadow-soft animate-pulse">
              <Heart className="h-12 w-12 text-primary" />
            </div>
          </div>
          
          <div className="space-y-4">
            <h1 className="text-6xl font-serif font-bold text-primary-dark">404</h1>
            <h2 className="text-2xl font-serif font-semibold text-primary-dark">Page Not Found</h2>
            <p className="text-lg text-foreground/70">
              Oops! We couldn't find the page you're looking for.
            </p>
            <p className="text-sm text-foreground/60">
              The page you requested could not be found. Please check the URL or use one of the navigation options below.
            </p>
          </div>

          <div className="space-y-4 pt-6">
            <Link href="/dashboard">
              <Button 
                className="w-full bg-primary hover:bg-primary-dark text-white shadow-soft hover:shadow-soft-lg transition-all duration-200"
                size="lg"
              >
                <Home className="mr-2 h-5 w-5" />
                Go to Dashboard
              </Button>
            </Link>
            
            <Link href="/couples">
              <Button 
                variant="outline" 
                className="w-full border-primary text-primary hover:bg-primary hover:text-white transition-all duration-200"
                size="lg"
              >
                <Users className="mr-2 h-5 w-5" />
                View Couples
              </Button>
            </Link>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-background text-foreground/50">or</span>
              </div>
            </div>

            <Link href="/login">
              <Button 
                variant="outline" 
                className="w-full text-foreground/70 hover:text-foreground border-border hover:bg-muted transition-all duration-200"
              >
                Return to Login
              </Button>
            </Link>
          </div>
        </div>

        <div className="pt-8 text-center">
          <p className="text-sm text-foreground/50">
            © 2024 Melbourne Celebrant Portal
          </p>
          <p className="text-xs text-foreground/40 mt-1">
            Made with ❤️ for Australian Marriage Celebrants
          </p>
        </div>
      </div>
    </div>
  );
} 