'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { unstable_noStore as noStore } from 'next/cache';
import InvoicePreviewModal from '@/components/InvoicePreviewModal';

interface Couple {
  id: number;
  partner1_name: string;
  partner2_name: string;
}

interface InvoiceItem {
  description: string;
  quantity: number;
  unit_cost: number;
}

interface InvoiceFormData {
  couple_id: number;
  invoice_date: string;
  invoice_ref: string;
  ceremony_date: string;
  venue: string;
  items: InvoiceItem[];
  gst: number;
  total: number;
}

export default function NewInvoicePage() {
  noStore();
  const router = useRouter();
  const { user } = useAuth();
  const [couples, setCouples] = useState<Couple[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [previewHtml, setPreviewHtml] = useState('');
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  const [formData, setFormData] = useState<InvoiceFormData>({
    couple_id: 0,
    invoice_date: new Date().toISOString().split('T')[0],
    invoice_ref: '',
    ceremony_date: '',
    venue: '',
    items: [{ description: '', quantity: 1, unit_cost: 0 }],
    gst: 0,
    total: 0,
  });

  useEffect(() => {
    const fetchCouples = async () => {
      try {
        const response = await fetch('/api/couples');
        if (!response.ok) throw new Error('Failed to fetch couples');
        const data = await response.json();
        setCouples(data);
      } catch (err) {
        setError('Failed to load couples');
        console.error(err);
      }
    };

    fetchCouples();
  }, []);

  const calculateTotals = (items: InvoiceItem[]) => {
    const subtotal = items.reduce((sum, item) => sum + (item.quantity * item.unit_cost), 0);
    const gst = subtotal * 0.1; // 10% GST
    const total = subtotal + gst;
    return { gst, total };
  };

  const handleItemChange = (index: number, field: keyof InvoiceItem, value: string | number) => {
    const newItems = [...formData.items];
    newItems[index] = {
      ...newItems[index],
      [field]: typeof value === 'string' && field !== 'description' ? parseFloat(value) || 0 : value,
    };

    const { gst, total } = calculateTotals(newItems);
    setFormData({
      ...formData,
      items: newItems,
      gst,
      total,
    });
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { description: '', quantity: 1, unit_cost: 0 }],
    });
  };

  const removeItem = (index: number) => {
    const newItems = formData.items.filter((_, i) => i !== index);
    const { gst, total } = calculateTotals(newItems);
    setFormData({
      ...formData,
      items: newItems,
      gst,
      total,
    });
  };

  const handlePreview = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/invoices/preview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          invoice_number: `PREVIEW-${Date.now()}`,
        }),
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/invoices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          invoice_number: `INV-${Date.now()}`,
        }),
      });

      if (!response.ok) throw new Error('Failed to create invoice');

      const data = await response.json();
      router.push(`/invoices/${data.id}`);
    } catch (err) {
      setError('Failed to create invoice');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <div>Please log in to create invoices.</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Create New Invoice</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Couple</label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
              value={formData.couple_id}
              onChange={(e) => setFormData({ ...formData, couple_id: parseInt(e.target.value) })}
              required
            >
              <option value="">Select a couple</option>
              {couples.map((couple) => (
                <option key={couple.id} value={couple.id}>
                  {couple.partner1_name} & {couple.partner2_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Invoice Date</label>
            <input
              type="date"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
              value={formData.invoice_date}
              onChange={(e) => setFormData({ ...formData, invoice_date: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Ceremony Date</label>
            <input
              type="date"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
              value={formData.ceremony_date}
              onChange={(e) => setFormData({ ...formData, ceremony_date: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Venue</label>
            <input
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
              value={formData.venue}
              onChange={(e) => setFormData({ ...formData, venue: e.target.value })}
              required
            />
          </div>
        </div>

        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Invoice Items</h2>
          {formData.items.map((item, index) => (
            <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <input
                  type="text"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                  value={item.description}
                  onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Quantity</label>
                <input
                  type="number"
                  min="1"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                  value={item.quantity}
                  onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Unit Cost ($)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gold-500 focus:ring-gold-500"
                  value={item.unit_cost}
                  onChange={(e) => handleItemChange(index, 'unit_cost', e.target.value)}
                  required
                />
              </div>
              {formData.items.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={addItem}
            className="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-gold-700 bg-gold-100 hover:bg-gold-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gold-500"
          >
            Add Item
          </button>
        </div>

        <div className="mt-8 space-y-4">
          <div className="flex justify-end">
            <div className="w-64">
              <div className="flex justify-between">
                <span>Subtotal:</span>
                <span>${(formData.total - formData.gst).toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>GST (10%):</span>
                <span>${formData.gst.toFixed(2)}</span>
              </div>
              <div className="flex justify-between font-bold">
                <span>Total:</span>
                <span>${formData.total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 flex justify-end space-x-4">
          <button
            type="button"
            onClick={handlePreview}
            disabled={loading}
            className="inline-flex items-center px-6 py-3 border border-gold-600 text-base font-medium rounded-md text-gold-600 bg-white hover:bg-gold-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gold-500"
          >
            {loading ? 'Loading...' : 'Preview Invoice'}
          </button>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-gold-600 hover:bg-gold-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gold-500"
          >
            {loading ? 'Creating...' : 'Create Invoice'}
          </button>
        </div>
      </form>

      <InvoicePreviewModal
        isOpen={isPreviewOpen}
        onClose={() => setIsPreviewOpen(false)}
        invoice={null}
      />
    </div>
  );
} 