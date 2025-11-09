import { CellSimple } from '@maxhub/max-ui'
import clsx from 'clsx'

type SideBarLinkProps = {
  icon: React.ReactNode
  title: string
  isActive: boolean
  showChevron?: boolean
  onClick: () => void
}

export function SideBarLink({
  icon,
  title,
  onClick,
  isActive = false,
  showChevron = true,
}: SideBarLinkProps) {
  return (
    <CellSimple
      before={icon}
      title={title}
      onClick={onClick}
      innerClassNames={{
        title: clsx({ 'text-(--accent-themed)': isActive }),
      }}
      showChevron={showChevron}
    />
  )
}
