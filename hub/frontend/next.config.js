/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  env: {
    NEXT_PUBLIC_HUB_URL: process.env.NEXT_PUBLIC_HUB_URL || 'http://localhost:8080',
  },
}

module.exports = nextConfig

