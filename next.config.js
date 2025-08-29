/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react']
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production'
  },
  swcMinify: true,
  // Removed output: 'standalone' for Vercel compatibility
}

module.exports = nextConfig