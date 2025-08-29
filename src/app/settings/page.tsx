'use client';

import React from 'react';
import Layout from '@/components/Layout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Settings, User } from 'lucide-react';
import { unstable_noStore as noStore } from 'next/cache';

export default function SettingsPage() {
  noStore();
  return (
    <ProtectedRoute>
      <Layout>
        <div className="space-y-6">
          <div>
            <h1 className="professional-header">Settings</h1>
            <p className="professional-subheader">Manage your account and preferences</p>
          </div>

          <div className="pro-card text-center py-12">
            <Settings className="w-16 h-16 text-secondary-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-secondary-950 mb-2">Coming Soon</h3>
            <p className="text-secondary-600 mb-6">
              Settings and preferences will be available in the next update
            </p>
            <button className="btn-primary flex items-center mx-auto">
              <User className="w-5 h-5 mr-2" />
              Update Profile
            </button>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
} 