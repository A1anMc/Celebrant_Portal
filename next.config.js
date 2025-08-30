/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configure API routes
  rewrites: async () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`
      }
    ]
  },
  images: {
    unoptimized: true
  },
  webpack: (config) => {
    config.module.rules.push({
      test: /\.(ico|png|jpg|jpeg|gif|svg)$/,
      type: 'asset/resource'
    })
    return config
  }
  // Removed CSP headers to fix eval blocking issue
}

module.exports = nextConfig 