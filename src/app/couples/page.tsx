'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Couple {
  id: number;
  partner1_name: string;
  partner2_name: string;
  wedding_date: string | null;
  status: string;
}

export default function CouplesPage() {
  const router = useRouter();
  const [couples, setCouples] = useState<Couple[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchCouples() {
      try {
        const response = await fetch('/api/couples');
        if (!response.ok) throw new Error('Failed to fetch couples');
        const data = await response.json();
        setCouples(data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchCouples();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">Couples</h1>
        <button
          onClick={() => router.push('/couples/new')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg"
        >
          New Couple
        </button>
      </div>

      <div className="bg-white rounded-lg shadow">
        <table className="min-w-full">
          <thead>
            <tr>
              <th className="px-6 py-3 text-left">Couple</th>
              <th className="px-6 py-3 text-left">Wedding Date</th>
              <th className="px-6 py-3 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {couples.map((couple) => (
              <tr 
                key={couple.id}
                onClick={() => router.push(`/couples/${couple.id}`)}
                className="hover:bg-gray-50 cursor-pointer"
              >
                <td className="px-6 py-4">
                  {couple.partner1_name} & {couple.partner2_name}
                </td>
                <td className="px-6 py-4">
                  {couple.wedding_date 
                    ? new Date(couple.wedding_date).toLocaleDateString()
                    : 'Not set'
                  }
                </td>
                <td className="px-6 py-4">
                  {couple.status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}