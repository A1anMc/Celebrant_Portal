'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { fetchDashboardData, addNote } from '@/lib/api';
import { unstable_noStore as noStore } from 'next/cache';
import ProtectedRoute from '@/components/ProtectedRoute';

interface DashboardData {
  quickStats: {
    thisWeekCeremonies: number;
    upcomingCeremonies: number;
    activeInquiries: number;
    bookedCouples: number;
  };
  thisWeeksCeremonies: any[];
  bookingFunnel: {
    inquiry: number;
    booked: number;
    completed: number;
  };
  revenueTrend: any[];
  latestInquiries: any[];
  notes: any[];
}

export default function DashboardPage() {
  noStore();
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [newNote, setNewNote] = useState('');

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const dashboardData = await fetchDashboardData();
        setData(dashboardData);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setIsLoading(false);
      }
    }

    // Only load dashboard data if user is authenticated and auth loading is complete
    if (!authLoading && user) {
      loadDashboardData();
    } else if (!authLoading && !user) {
      // User is not authenticated, stop loading
      setIsLoading(false);
    }
  }, [authLoading, user]);

  const handleAddNote = async () => {
    if (!newNote.trim()) return;

    try {
      await addNote(newNote);
      
      // Refresh dashboard data
      const dashboardData = await fetchDashboardData();
      setData(dashboardData);
      setNewNote('');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  if (authLoading || isLoading || !data) {
    return <div>Loading...</div>;
  }

  return (
    <ProtectedRoute>
      <div className="p-6 max-w-7xl mx-auto">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-semibold">
            👋 Welcome Back, {user?.full_name || 'Celebrant'}
          </h1>
          <p className="text-gray-600 mt-2">
            Here&apos;s what&apos;s happening in your celebrant business
          </p>
        </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-2">This Week&apos;s Ceremonies</h3>
          <p className="text-3xl font-bold text-blue-600">
            {data.quickStats.thisWeekCeremonies}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-2">Upcoming Ceremonies</h3>
          <p className="text-3xl font-bold text-green-600">
            {data.quickStats.upcomingCeremonies}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-2">Active Inquiries</h3>
          <p className="text-3xl font-bold text-purple-600">
            {data.quickStats.activeInquiries}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-2">Booked Couples</h3>
          <p className="text-3xl font-bold text-orange-600">
            {data.quickStats.bookedCouples}
          </p>
        </div>
      </div>

      {/* This Week's Ceremonies Timeline */}
      <div className="bg-white rounded-lg shadow mb-8 p-6">
        <h2 className="text-xl font-semibold mb-4">📆 This Week&apos;s Ceremonies</h2>
        {data.thisWeeksCeremonies.length > 0 ? (
          <div className="space-y-4">
            {data.thisWeeksCeremonies.map((ceremony) => (
              <div
                key={ceremony.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div>
                  <h3 className="font-medium">
                    {ceremony.partner1_name} &amp; {ceremony.partner2_name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {new Date(ceremony.wedding_date).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => router.push(`/couples/${ceremony.id}`)}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg"
                >
                  View Details
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No ceremonies scheduled for this week</p>
        )}
      </div>

      {/* Booking Funnel and Revenue */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Booking Funnel */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">🔄 Booking Funnel</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>Inquiries</span>
              <span className="font-medium">{data.bookingFunnel.inquiry}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Booked</span>
              <span className="font-medium">{data.bookingFunnel.booked}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Completed</span>
              <span className="font-medium">{data.bookingFunnel.completed}</span>
            </div>
          </div>
        </div>

        {/* Revenue Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">💸 Revenue Trend</h2>
          <div className="h-64">
            {/* Add your preferred charting library here */}
            <p className="text-gray-600">Revenue visualization coming soon</p>
          </div>
        </div>
      </div>

      {/* Notes and Latest Inquiries */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Notes */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">💬 Notes & Reminders</h2>
          <div className="mb-4">
            <textarea
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Add a new note..."
              className="w-full p-2 border rounded-lg"
              rows={3}
            />
            <button
              onClick={handleAddNote}
              className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg"
            >
              Add Note
            </button>
          </div>
          <div className="space-y-4">
            {data.notes.map((note) => (
              <div key={note.id} className="p-4 bg-gray-50 rounded-lg">
                <p>{note.content}</p>
                <p className="text-sm text-gray-600 mt-2">
                  {new Date(note.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Latest Inquiries */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">📬 Latest Inquiries</h2>
          <div className="space-y-4">
            {data.latestInquiries.map((inquiry) => (
              <div
                key={inquiry.id}
                className="p-4 bg-gray-50 rounded-lg cursor-pointer"
                onClick={() => router.push(`/couples/${inquiry.id}`)}
              >
                <h3 className="font-medium">
                  {inquiry.partner1_name} & {inquiry.partner2_name}
                </h3>
                <p className="text-sm text-gray-600">
                  Received: {new Date(inquiry.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
    </ProtectedRoute>
  );
} 