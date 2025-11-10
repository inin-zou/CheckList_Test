import type { Metadata } from 'next'
import './globals.css'
import Iridescence from '@/components/Iridescence'

export const metadata: Metadata = {
  title: 'CheckList App',
  description: 'Checklist management application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Iridescence
          color={[1, 1, 1]}
          mouseReact={false}
          amplitude={0.1}
          speed={1.0}
        />
        {children}
      </body>
    </html>
  )
}