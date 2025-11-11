import { CellHeader, CellList, Flex, Typography } from '@maxhub/max-ui'
import clsx from 'clsx'
import { ChevronDown } from 'lucide-react'
import { useState } from 'react'

export function SideBarSection({
  title,
  children,
}: {
  title: React.ReactNode
  children: React.ReactNode
}) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <CellList mode="island" filled>
      <CellHeader
        className="cursor-pointer h-12"
        onClick={() => setIsOpen(!isOpen)}
        titleStyle="normal"
        after={
          <ChevronDown
            size={18}
            className={clsx('transition-transform duration-100', {
              '-rotate-90': !isOpen,
            })}
          />
        }
      >
        {title}
      </CellHeader>
      {isOpen && <>{children}</>}
    </CellList>
  )
}
