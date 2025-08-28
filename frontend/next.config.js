/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configure API routes
  rewrites: async () => {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*'
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
}

module.exports = nextConfig 