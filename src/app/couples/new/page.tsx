'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface FormData {
  partner1_name: string;
  partner1_email: string;
  partner2_name: string;
  partner2_email: string;
  wedding_date: string;
  venue: string;
  ceremony_type: string;
  status: string;
}

export default function NewCouplePage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    partner1_name: '',
    partner1_email: '',
    partner2_name: '',
    partner2_email: '',
    wedding_date: '',
    venue: '',
    ceremony_type: 'Wedding',
    status: 'Inquiry',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch('/api/couples', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to create couple');
      }

      router.push('/couples');
    } catch (error) {
      console.error('Error:', error);
      // Add error handling UI here
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-6">New Couple</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-4">
          <h2 className="text-lg font-medium">Partner 1</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              name="partner1_name"
              value={formData.partner1_name}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              name="partner1_email"
              value={formData.partner1_email}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              required
            />
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-medium">Partner 2</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              name="partner2_name"
              value={formData.partner2_name}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              name="partner2_email"
              value={formData.partner2_email}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              required
            />
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-medium">Wedding Details</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700">Wedding Date</label>
            <input
              type="date"
              name="wedding_date"
              value={formData.wedding_date}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Venue</label>
            <input
              type="text"
              name="venue"
              value={formData.venue}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Ceremony Type</label>
            <select
              name="ceremony_type"
              value={formData.ceremony_type}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            >
              <option value="Wedding">Wedding</option>
              <option value="Elopement">Elopement</option>
              <option value="Commitment">Commitment Ceremony</option>
              <option value="Vow Renewal">Vow Renewal</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            >
              <option value="Inquiry">Inquiry</option>
              <option value="Booked">Booked</option>
              <option value="Completed">Completed</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            {isSubmitting ? 'Creating...' : 'Create Couple'}
          </button>
        </div>
      </form>
    </div>
  );
} 