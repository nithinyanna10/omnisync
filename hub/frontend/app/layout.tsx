import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'OmniSync Hub',
  description: 'Visualization and control center for OmniSync Protocol',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

