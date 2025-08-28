'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { unstable_noStore as noStore } from 'next/cache';

interface InvoiceSettings {
  defaultItems: {
    deposit: string;
    solemnisation: string;
    mcServices: string;
    travel: string;
    bdmCertificate: string;
  };
  paymentInstructions: {
    title: string;
    transferInstructions: string;
    referenceInstructions: string;
  };
  footer: {
    businessName: string;
    title: string;
    address: string;
    email: string;
  };
}

export default function InvoiceSettingsPage() {
  noStore();
  const { user } = useAuth();
  const [settings, setSettings] = useState<InvoiceSettings>({
    defaultItems: {
      deposit: 'Deposit for Marriage Celebrant Booking (10%)',
      solemnisation: 'Solemnisation of Marriage by Civil Marriage Celebrant & Administration and documentation of all Marriage documents',
      mcServices: 'MC SERVICES ($200/hr, 3hr minimum) :',
      travel: 'Travel:',
      bdmCertificate: 'BDM Certificate',
    },
    paymentInstructions: {
      title: 'Payment',
      transferInstructions: 'Payments can be made via electronic transfer to:',
      referenceInstructions: 'Please include invoice number as reference',
    },
    footer: {
      businessName: 'A Melbourne Celebrant',
      title: 'Director & Celebrant',
      address: '1A Hunter Street Brunswick West',
      email: 'hello@amelbournecelebrant.com.au',
    },
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await fetch('/api/invoice-settings');
        if (!response.ok) throw new Error('Failed to fetch settings');
        const data = await response.json();
        setSettings(data);
      } catch (err) {
        setError('Failed to load settings');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  const handleChange = (section: keyof InvoiceSettings, field: string, value: string) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await fetch('/api/invoice-settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      if (!response.ok) throw new Error('Failed to save settings');
      
      setSuccessMessage('Settings saved successfully');
    } catch (err) {
      setError('Failed to save settings');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (!user) {
    return <div>Please log in to access settings.</div>;
  }

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Invoice Template Settings</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {successMessage}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Default Invoice Items</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Deposit Description</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.defaultItems.deposit}
                onChange={(e) => handleChange('defaultItems', 'deposit', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Solemnisation Description</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.defaultItems.solemnisation}
                onChange={(e) => handleChange('defaultItems', 'solemnisation', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">MC Services Description</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.defaultItems.mcServices}
                onChange={(e) => handleChange('defaultItems', 'mcServices', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Travel Description</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.defaultItems.travel}
                onChange={(e) => handleChange('defaultItems', 'travel', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">BDM Certificate Description</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.defaultItems.bdmCertificate}
                onChange={(e) => handleChange('defaultItems', 'bdmCertificate', e.target.value)}
              />
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-4">Payment Instructions</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Payment Section Title</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.paymentInstructions.title}
                onChange={(e) => handleChange('paymentInstructions', 'title', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Transfer Instructions</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.paymentInstructions.transferInstructions}
                onChange={(e) => handleChange('paymentInstructions', 'transferInstructions', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Reference Instructions</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.paymentInstructions.referenceInstructions}
                onChange={(e) => handleChange('paymentInstructions', 'referenceInstructions', e.target.value)}
              />
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-4">Footer Information</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Business Name</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.footer.businessName}
                onChange={(e) => handleChange('footer', 'businessName', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Title</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.footer.title}
                onChange={(e) => handleChange('footer', 'title', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Address</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.footer.address}
                onChange={(e) => handleChange('footer', 'address', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                value={settings.footer.email}
                onChange={(e) => handleChange('footer', 'email', e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-gold-600 hover:bg-gold-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gold-500"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );
} 