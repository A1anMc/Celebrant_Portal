import './globals.css'
import { Inter } from 'next/font/google'
import { Metadata } from 'next'
import { AuthProvider } from '@/contexts/AuthContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Melbourne Celebrant Portal',
  description: 'Professional wedding celebrant management system',
  icons: {
    icon: [
      {
        url: '/favicon.ico',
        sizes: '32x32',
        type: 'image/x-icon',
      }
    ]
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="icon"
          href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>💍</text></svg>"
        />
      </head>
      <body>{children}</body>
    </html>
  )
} 