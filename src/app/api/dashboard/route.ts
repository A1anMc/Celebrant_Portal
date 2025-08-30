import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    const token = authHeader?.replace('Bearer ', '');
    
    if (!token) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Fetch all required data in parallel
    const [couplesResponse, invoicesResponse, notesResponse] = await Promise.all([
      fetch(`${API_URL}/api/v1/couples/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }),
      fetch(`${API_URL}/api/v1/invoices/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }),
      fetch(`${API_URL}/api/v1/notes/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }),
    ]);

    // Check if any of the responses indicate authentication failure
    if (couplesResponse.status === 401 || invoicesResponse.status === 401 || notesResponse.status === 401) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    if (!couplesResponse.ok || !invoicesResponse.ok || !notesResponse.ok) {
      throw new Error('Failed to fetch dashboard data');
    }

    const [couples, invoices, notes] = await Promise.all([
      couplesResponse.json(),
      invoicesResponse.json(),
      notesResponse.json(),
    ]);

    // Calculate quick stats
    const now = new Date();
    const thisWeek = couples.filter((couple: any) => {
      const weddingDate = new Date(couple.wedding_date);
      const diffTime = weddingDate.getTime() - now.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays >= 0 && diffDays <= 7;
    });

    const upcomingCeremonies = couples.filter((couple: any) => {
      const weddingDate = new Date(couple.wedding_date);
      return weddingDate > now;
    });

    const inquiries = couples.filter((couple: any) => 
      couple.status === 'Inquiry'
    );

    const bookedCouples = couples.filter((couple: any) => 
      couple.status === 'Booked'
    );

    // Calculate revenue trend (last 6 months)
    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);

    const revenueTrend = invoices.filter((invoice: any) => 
      new Date(invoice.date) >= sixMonthsAgo
    );

    return NextResponse.json({
      quickStats: {
        thisWeekCeremonies: thisWeek.length,
        upcomingCeremonies: upcomingCeremonies.length,
        activeInquiries: inquiries.length,
        bookedCouples: bookedCouples.length,
      },
      thisWeeksCeremonies: thisWeek,
      bookingFunnel: {
        inquiry: inquiries.length,
        booked: bookedCouples.length,
        completed: couples.filter((c: any) => c.status === 'Completed').length,
      },
      revenueTrend,
      latestInquiries: inquiries.slice(0, 5),
      notes: notes.slice(0, 5),
    });
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch dashboard data' },
      { status: 500 }
    );
  }
} 