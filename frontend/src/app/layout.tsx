import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Legal Document Assistant',
  description: 'Enterprise Legal Tech System with Hybrid Search and Dual-Agent Pipeline',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="min-h-screen bg-background text-foreground selection:bg-accent/30 antialiased">
        {children}
      </body>
    </html>
  )
}
