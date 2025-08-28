import type { Metadata } from 'next'
import { Funnel_Display } from 'next/font/google'
import './globals.css'

const funnelDisplay = Funnel_Display({ 
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-funnel-display'
})

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
      <body className={funnelDisplay.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
          {children}
        </div>
      </body>
    </html>
  )
}
