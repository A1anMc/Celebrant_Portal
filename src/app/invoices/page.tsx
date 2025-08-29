'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { unstable_noStore as noStore } from 'next/cache';

interface Invoice {
  id: number;
  invoice_number: string;
  invoice_date: string;
  couple: {
    partner1_name: string;
    partner2_name: string;
  };
  total: number;
}

export default function InvoicesPage() {
  noStore();
  const { user } = useAuth();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        const response = await fetch('/api/invoices');
        if (!response.ok) throw new Error('Failed to fetch invoices');
        const data = await response.json();
        setInvoices(data);
      } catch (err) {
        setError('Failed to load invoices');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchInvoices();
  }, []);

  if (!user) {
    return <div>Please log in to view invoices.</div>;
  }

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div className="text-red-600">{error}</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Invoices</h1>
        <Link
          href="/invoices/new"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-gold-600 hover:bg-gold-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gold-500"
        >
          Create New Invoice
        </Link>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Invoice Number
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Couple
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {invoices.map((invoice) => (
              <tr key={invoice.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {invoice.invoice_number}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(invoice.invoice_date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {invoice.couple.partner1_name} & {invoice.couple.partner2_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                  ${invoice.total.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link
                    href={`/invoices/${invoice.id}`}
                    className="text-gold-600 hover:text-gold-900 mr-4"
                  >
                    View
                  </Link>
                  <button
                    onClick={async () => {
                      try {
                        const response = await fetch(`/api/invoices/${invoice.id}/pdf`);
                        if (!response.ok) throw new Error('Failed to generate PDF');

                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `invoice-${invoice.invoice_number}.pdf`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                      } catch (err) {
                        console.error('Failed to download PDF:', err);
                      }
                    }}
                    className="text-gold-600 hover:text-gold-900"
                  >
                    Download PDF
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}