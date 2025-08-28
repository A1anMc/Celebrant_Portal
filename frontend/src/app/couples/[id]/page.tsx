'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Couple {
  id: number;
  partner1_name: string;
  partner1_email: string;
  partner2_name: string;
  partner2_email: string;
  wedding_date: string | null;
  venue: string | null;
  ceremony_type: string;
  status: string;
  created_at: string;
  updated_at: string | null;
}

export default function CouplePage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const [couple, setCouple] = useState<Couple | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCouple() {
      try {
        const { id } = await params;
        const response = await fetch(`/api/couples/${id}`);
        if (!response.ok) throw new Error('Failed to fetch couple');
        const data = await response.json();
        setCouple(data);
      } catch (error) {
        console.error('Error:', error);
        setError('Failed to load couple details');
      } finally {
        setIsLoading(false);
      }
    }

    fetchCouple();
  }, [params]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error || !couple) {
    return <div className="text-red-600">{error || 'Couple not found'}</div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">
          {couple.partner1_name} & {couple.partner2_name}
        </h1>
        <button
          onClick={() => router.push('/couples')}
          className="px-4 py-2 border border-gray-300 rounded-md text-sm"
        >
          Back to Couples
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h2 className="text-lg font-medium mb-4">Partner 1</h2>
            <div className="space-y-2">
              <p>
                <span className="font-medium">Name:</span> {couple.partner1_name}
              </p>
              <p>
                <span className="font-medium">Email:</span> {couple.partner1_email}
              </p>
            </div>
          </div>

          <div>
            <h2 className="text-lg font-medium mb-4">Partner 2</h2>
            <div className="space-y-2">
              <p>
                <span className="font-medium">Name:</span> {couple.partner2_name}
              </p>
              <p>
                <span className="font-medium">Email:</span> {couple.partner2_email}
              </p>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-lg font-medium mb-4">Wedding Details</h2>
          <div className="space-y-2">
            <p>
              <span className="font-medium">Date:</span>{' '}
              {couple.wedding_date
                ? new Date(couple.wedding_date).toLocaleDateString()
                : 'Not set'}
            </p>
            <p>
              <span className="font-medium">Venue:</span>{' '}
              {couple.venue || 'Not set'}
            </p>
            <p>
              <span className="font-medium">Ceremony Type:</span>{' '}
              {couple.ceremony_type}
            </p>
            <p>
              <span className="font-medium">Status:</span>{' '}
              <span className="px-2 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                {couple.status}
              </span>
            </p>
          </div>
        </div>

        <div className="border-t pt-6">
          <div className="flex justify-end space-x-4">
            <button
              onClick={async () => {
                const { id } = await params;
                router.push(`/couples/${id}/edit`);
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Edit Details
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 