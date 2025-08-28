/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    GITHUB_CLIENT_ID: process.env.GITHUB_CLIENT_ID,
    QUILT_API_URL: process.env.QUILT_API_URL || 'https://quilt-production.up.railway.app',
  },
}

module.exports = nextConfig
