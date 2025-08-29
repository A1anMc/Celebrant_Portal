'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import InvoicePreviewModal from '@/components/InvoicePreviewModal';
import { unstable_noStore as noStore } from 'next/cache';

interface InvoiceItem {
  id: number;
  description: string;
  quantity: number;
  unit_cost: number;
}

interface Invoice {
  id: number;
  couple: {
    id: number;
    partner1_name: string;
    partner2_name: string;
  };
  invoice_number: string;
  invoice_date: string;
  invoice_ref: string;
  ceremony_date: string;
  venue: string;
  items: InvoiceItem[];
  gst: number;
  total: number;
}

export default function InvoiceDetailPage() {
  noStore();
  const { id } = useParams();
  const { user } = useAuth();
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [previewHtml, setPreviewHtml] = useState('');
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  useEffect(() => {
    const fetchInvoice = async () => {
      try {
        const response = await fetch(`/api/invoices/${id}`);
        if (!response.ok) throw new Error('Failed to fetch invoice');
        const data = await response.json();
        setInvoice(data);
      } catch (err) {
        setError('Failed to load invoice');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchInvoice();
    }
  }, [id]);

  const handlePreview = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/invoices/preview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(invoice),
      });

      if (!response.ok) throw new Error('Failed to generate preview');

      const html = await response.text();
      setPreviewHtml(html);
      setIsPreviewOpen(true);
    } catch (err) {
      setError('Failed to generate preview');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async () => {
    try {
      const response = await fetch(`/api/invoices/${id}/pdf`);
      if (!response.ok) throw new Error('Failed to generate PDF');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice-${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download PDF');
      console.error(err);
    }
  };

  if (!user) {
    return <div>Please log in to view invoices.</div>;
  }

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div className="text-red-600">{error}</div>;
  }

  if (!invoice) {
    return <div>Invoice not found</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Invoice #{invoice.invoice_number}</h1>
        <div className="flex space-x-4">
          <button
            onClick={handlePreview}
            className="inline-flex items-center px-4 py-2 border border-gold-600 text-sm font-medium rounded-md text-gold-600 bg-white hover:bg-gold-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gold-500"
          >
            Preview
          </button>
          <button
            onClick={downloadPDF}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-gold-600 hover:bg-gold-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gold-500"
          >
            Download PDF
          </button>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Invoice Details</h3>
        </div>
        <div className="border-t border-gray-200">
          <dl>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Couple</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {invoice.couple.partner1_name} & {invoice.couple.partner2_name}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Invoice Date</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {new Date(invoice.invoice_date).toLocaleDateString()}
              </dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Ceremony Date</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {new Date(invoice.ceremony_date).toLocaleDateString()}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Venue</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {invoice.venue}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Invoice Items</h2>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Quantity
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Unit Cost
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {invoice.items.map((item) => (
              <tr key={item.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {item.description}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                  {item.quantity}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                  ${item.unit_cost.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                  ${(item.quantity * item.unit_cost).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-gray-50">
            <tr>
              <td colSpan={3} className="px-6 py-4 text-sm text-gray-500 text-right">
                Subtotal
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                ${(invoice.total - invoice.gst).toFixed(2)}
              </td>
            </tr>
            <tr>
              <td colSpan={3} className="px-6 py-4 text-sm text-gray-500 text-right">
                GST (10%)
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                ${invoice.gst.toFixed(2)}
              </td>
            </tr>
            <tr className="font-bold">
              <td colSpan={3} className="px-6 py-4 text-sm text-gray-900 text-right">
                Total
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                ${invoice.total.toFixed(2)}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>

      <InvoicePreviewModal
        isOpen={isPreviewOpen}
        onClose={() => setIsPreviewOpen(false)}
        invoice={invoice}
      />
    </div>
  );
} 