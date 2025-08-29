'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { unstable_noStore as noStore } from 'next/cache';

export default function Home() {
  noStore();
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (user) {
        router.push('/dashboard');
      } else {
        router.push('/login');
      }
    }
  }, [user, loading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
      <div className="text-center">
        <div className="loading-spinner w-12 h-12 border-primary-500 mx-auto mb-4"></div>
        <p className="text-secondary-600 font-medium">Loading...</p>
      </div>
    </div>
  );
} 