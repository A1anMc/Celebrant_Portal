'use client';

import React from 'react';
import Layout from '@/components/Layout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { FileText, Plus } from 'lucide-react';
import { unstable_noStore as noStore } from 'next/cache';

export default function TemplatesPage() {
  noStore();
  return (
    <ProtectedRoute>
      <Layout>
        <div className="space-y-6">
          <div>
            <h1 className="professional-header">Ceremony Templates</h1>
            <p className="professional-subheader">Manage your ceremony scripts and templates</p>
          </div>

          <div className="pro-card text-center py-12">
            <FileText className="w-16 h-16 text-secondary-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-secondary-950 mb-2">Coming Soon</h3>
            <p className="text-secondary-600 mb-6">
              Ceremony templates feature will be available in the next update
            </p>
            <button className="btn-primary flex items-center mx-auto">
              <Plus className="w-5 h-5 mr-2" />
              Create Template
            </button>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
}