/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  distDir: '.next',
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  env: {
    // In unified deployment, API is on the same host
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || (
      process.env.NODE_ENV === 'production' 
        ? '' // Same host in production
        : 'http://localhost:8000' // Separate in development
    ),
  },
  async rewrites() {
    // In unified deployment, no rewrites needed as FastAPI handles routing
    if (process.env.NODE_ENV === 'production') {
      return [];
    }
    // Only rewrite in development
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
  reactStrictMode: true,
  // Disable x-powered-by header
  poweredByHeader: false,
  // Optimize for production
  compress: true,
  // Configure for unified deployment
  experimental: {
    outputFileTracingRoot: process.env.NODE_ENV === 'production' ? '/app' : undefined,
  },
};

module.exports = nextConfig;
