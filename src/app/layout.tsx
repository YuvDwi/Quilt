import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Quilt - Vector Database for the Web',
  description: 'Deploy and index your repositories with pre-computed vector embeddings for instant semantic search',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Parkinsans:wght@300;400;500;600;700&family=Sacramento&display=swap" rel="stylesheet" />
      </head>
      <body>
        {children}
      </body>
    </html>
  )
}
