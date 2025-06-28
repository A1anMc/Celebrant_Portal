'use client';

import { Suspense } from 'react';
import CouplesPageContent from './CouplesPageContent';

export default function CouplesPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    }>
      <CouplesPageContent />
    </Suspense>
  );
} 