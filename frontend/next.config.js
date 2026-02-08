/** @type {import('next').NextConfig} */
const nextConfig = {
 // reactStrictMode: true,
  // swcMinify: true, // This is a valid option in newer Next.js versions
  experimental: {
  //  serverActions: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

module.exports = nextConfig;