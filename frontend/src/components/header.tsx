import { Flex, IconButton, Typography } from '@maxhub/max-ui'
import { MenuSquare } from 'lucide-react'
import React, { useState } from 'react'
import { useLocation } from '@tanstack/react-router'
import { SideBar } from './side-bar'
import { routes } from '@/routes'

export function Header({
  children,
}: {
  children?: React.ReactNode | undefined
}) {
  const location = useLocation()
  const [isOpen, setIsOpen] = useState(false)

  const route =
    location.pathname in routes ? routes[location.pathname] : undefined

  return (
    <>
      <header className="z-1 w-full px-2 py-3 sticky top-0 bg-(--background-surface-primary) flex justify-between">
        <Flex align="center" gapX={16}>
          <IconButton mode="tertiary" onClick={() => setIsOpen(true)}>
            <MenuSquare size={24} />
          </IconButton>
          <Typography.Headline>{route?.title}</Typography.Headline>
        </Flex>
        {children}
      </header>

      <SideBar isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  )
}
