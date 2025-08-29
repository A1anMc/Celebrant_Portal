import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(request: NextRequest) {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('token');

    if (!token) {
      return NextResponse.json(
        { error: 'No token found' },
        { status: 401 }
      );
    }

    // Here you would typically validate the token with your backend
    // For now, we'll return a mock user
    const mockUser = {
      id: 1,
      email: 'celebrant@example.com',
      full_name: 'John Celebrant',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return NextResponse.json(mockUser);
  } catch (error) {
    console.error('Auth check error:', error);
    return NextResponse.json(
      { error: 'Authentication failed' },
      { status: 500 }
    );
  }
} 