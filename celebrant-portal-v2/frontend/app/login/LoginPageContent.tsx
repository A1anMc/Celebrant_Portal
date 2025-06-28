'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '../../src/contexts/AuthContext';
import { Button } from '../../src/components/ui/Button';
import { Input } from '../../src/components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/Card';
import { Heart, Mail, Lock, Eye, EyeOff, ArrowRight } from 'lucide-react';

export default function LoginPageContent() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login, user } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const from = searchParams.get('from') || '/dashboard';

  useEffect(() => {
    // Clear any existing error when component mounts
    setError('');
    
    if (user) {
      router.push(from);
    }
  }, [user, router, from]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ email, password });
      router.push(from);
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed. Please check your credentials and try again.');
      // Clear password on error
      setPassword('');
    } finally {
      setIsLoading(false);
    }
  };

  const fillDemoCredentials = () => {
    setEmail('admin@melbournecelebrant.com');
    setPassword('admin123');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-secondary via-background to-accent-light py-12 px-4 sm:px-6 lg:px-8 animate-fade-in">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <div className="bg-primary/10 p-4 rounded-full shadow-soft animate-slide-up">
              <Heart className="h-10 w-10 text-primary" />
            </div>
          </div>
          <h2 className="text-4xl font-serif font-bold text-primary-dark animate-slide-up" style={{ animationDelay: '100ms' }}>
            Melbourne Celebrant Portal
          </h2>
          <p className="mt-3 text-lg text-foreground/70 animate-slide-up" style={{ animationDelay: '200ms' }}>
            Welcome back to your celebration hub
          </p>
        </div>

        <Card className="shadow-soft-lg border-border/50 animate-slide-up" style={{ animationDelay: '300ms' }}>
          <CardHeader className="text-center pb-6">
            <CardTitle className="text-2xl font-serif text-primary-dark">Sign In</CardTitle>
            <CardDescription className="text-base">
              Enter your credentials to access your celebrant portal
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-lg text-sm flex items-center gap-2 animate-slide-down">
                  <svg className="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span>{error}</span>
                </div>
              )}

              <div className="space-y-5">
                <Input
                  label="Email Address"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="Enter your email address"
                  autoComplete="email"
                  leftIcon={<Mail className="h-4 w-4" />}
                  className="h-12 text-base"
                />

                <Input
                  label="Password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  leftIcon={<Lock className="h-4 w-4" />}
                  rightIcon={
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="text-foreground/50 hover:text-foreground/70 transition-colors"
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  }
                  className="h-12 text-base"
                />
              </div>

              <Button
                type="submit"
                className="w-full h-12 bg-primary hover:bg-primary-dark text-white text-base font-semibold shadow-soft hover:shadow-soft-lg transition-all duration-200"
                disabled={isLoading || !email || !password}
                loading={isLoading}
              >
                {isLoading ? 'Signing in...' : (
                  <>
                    Sign In
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </form>

            <div className="mt-8 p-4 bg-muted/30 rounded-lg border border-border/30">
              <div className="text-center">
                <p className="text-sm text-foreground/70 mb-3 font-medium">
                  Demo Access Available
                </p>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={fillDemoCredentials}
                  className="text-xs hover:bg-primary/5 border-primary/30"
                >
                  Use Demo Credentials
                </Button>
                <p className="text-xs text-foreground/50 mt-2">
                  admin@melbournecelebrant.com / admin123
                </p>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-border/30">
              <p className="text-sm font-medium text-foreground/80 mb-3 text-center">
                What you'll access:
              </p>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="flex items-center gap-2 text-foreground/60">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Couple Management</span>
                </div>
                <div className="flex items-center gap-2 text-foreground/60">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Ceremony Planning</span>
                </div>
                <div className="flex items-center gap-2 text-foreground/60">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Legal Compliance</span>
                </div>
                <div className="flex items-center gap-2 text-foreground/60">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Invoice Management</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="text-center animate-slide-up" style={{ animationDelay: '400ms' }}>
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