import { Flex, IconButton } from '@maxhub/max-ui'
import { useRouter } from '@tanstack/react-router'
import clsx from 'clsx'
import { ChevronLeft } from 'lucide-react'
import type React from 'react'

export function DynamicPageLayout({
  heading,
  children,
  footer,
  screenHeight,
}: {
  children: React.ReactNode
  heading?: React.ReactNode | undefined
  footer?: React.ReactNode | undefined
  screenHeight?: boolean
}) {
  const router = useRouter()
  return (
    <Flex
      direction="column"
      className={clsx({ 'h-screen': screenHeight })}
      gap={24}
    >
      <header className="z-1 w-full px-2 py-3 sticky top-0 bg-(--background-surface-primary) flex space-x-6 items-center">
        <IconButton
          type="button"
          mode="link"
          onClick={() => router.history.back()}
        >
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
