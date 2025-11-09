import { CellHeader, CellList, Typography } from '@maxhub/max-ui'
import clsx from 'clsx'
import { ChevronDown } from 'lucide-react'
import { useState } from 'react'

export function SideBarSection({
  title,
  children,
}: {
  title: string
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
        <Typography.Title className="text-sm!">{title}</Typography.Title>
      </CellHeader>
      {isOpen && <>{children}</>}
    </CellList>
  )
}
