import { Flex, IconButton } from '@maxhub/max-ui'
import { useRouter } from '@tanstack/react-router'
import { ChevronLeft } from 'lucide-react'
import type React from 'react'

export function DynamicPageLayout({
  heading,
  children,
  footer,
}: {
  children: React.ReactNode
  heading?: React.ReactNode | undefined
  footer?: React.ReactNode | undefined
}) {
  const router = useRouter()
  return (
    <Flex direction="column" gap={24}>
      <header className="z-1 w-full px-2 py-3 sticky top-0 bg-(--background-surface-primary) flex space-x-6 items-center">
        <IconButton mode="link" onClick={() => router.history.back()}>
          <ChevronLeft size={24} />
        </IconButton>
        {heading}
      </header>
      <main className="w-full h-full">{children}</main>
      <footer className="z-1 fixed bottom-0 w-full max-w-[1440px]">
        {footer}
      </footer>
    </Flex>
  )
}
