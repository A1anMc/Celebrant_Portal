import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://amelbournecelebrant-6ykh.onrender.com',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'https://amelbournecelebrant-6ykh.onrender.com'}/:path*`,
      },
    ];
  },
};

export default nextConfig;
