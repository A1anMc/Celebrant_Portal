import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Log route information
  console.log('Middleware - Path:', request.nextUrl.pathname)

  // Check if the request is for the API
  if (request.nextUrl.pathname.startsWith('/api/')) {
    return NextResponse.next()
  }

  // Get token from cookies
  const token = request.cookies.get('token')

  // Define protected routes that require authentication
  const protectedRoutes = [
    '/dashboard',
    '/couples',
    '/templates',
    '/legal-forms',
    '/invoices',
    '/settings'
  ]

  // Public routes that don't require authentication
  const publicRoutes = ['/', '/login', '/beta']

  // Check if the current path is a protected route
  const isProtectedRoute = protectedRoutes.some(route => 
    request.nextUrl.pathname === route || 
    request.nextUrl.pathname.startsWith(`${route}/`)
  )

  // Check if the current path is a public route
  const isPublicRoute = publicRoutes.some(route => 
    request.nextUrl.pathname === route || 
    request.nextUrl.pathname.startsWith(`${route}/`)
  )

  // Skip middleware for Next.js internal routes and static files
  if (
    request.nextUrl.pathname.startsWith('/_next/') ||
    request.nextUrl.pathname.includes('/api/') ||
    request.nextUrl.pathname.includes('.') ||
    request.nextUrl.pathname === '/favicon.ico'
  ) {
    return NextResponse.next()
  }

  // If no token and trying to access protected route, redirect to login
  if (!token && isProtectedRoute) {
    console.log('No token, redirecting to login')
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', request.nextUrl.pathname)
    return NextResponse.redirect(loginUrl)
  }

  // If has token and trying to access login, redirect to dashboard
  if (token && request.nextUrl.pathname === '/login') {
    console.log('Has token, redirecting to dashboard')
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // Allow access to all other routes
  return NextResponse.next()
}

// Configure the paths that should trigger the middleware
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
} 