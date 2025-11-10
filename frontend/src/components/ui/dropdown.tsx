import clsx from 'clsx'
import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react'

type DropdownContextProps = {
  open: boolean
  setOpen: (o: boolean) => void
}

const DropdownContext = createContext<DropdownContextProps | null>(null)

function useDropdownContext() {
  const ctx = useContext(DropdownContext)
  if (!ctx) {
    throw new Error('useDropdownContext must be used within DropDown')
  }
  return ctx
}

type DropDownProps = {
  children: ReactNode
  className?: string
}

export function DropDown({ children, className }: DropDownProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <DropdownContext.Provider value={{ open, setOpen }}>
      <div ref={ref} className={clsx('relative inline-block', className)}>
        {children}
      </div>
    </DropdownContext.Provider>
  )
}

type DropDownTriggerProps = {
  children: ReactNode
  className?: string
  disabled?: boolean
}

DropDown.Trigger = function Trigger({
  children,
  className,
  disabled,
}: DropDownTriggerProps) {
  const { open, setOpen } = useDropdownContext()

  return (
    <div
      onClick={() => !disabled && setOpen(!open)}
      className={clsx(className)}
    >
      {children}
    </div>
  )
}

type DropDownContentProps = {
  children: ReactNode
  className?: string
}

DropDown.Content = function Content({
  children,
  className,
}: DropDownContentProps) {
  const { open } = useDropdownContext()
  if (!open) return null
  return (
    <div
      className={clsx(
        `
        absolute z-10 rounded-(--size-border-radius-semantic-border-radius-card)
        bg-(--background-surface-card)
      `,
        className,
      )}
    >
      {children}
    </div>
  )
}

type DropDownItemProps = {
  children: ReactNode
  className?: string
  onClick?: () => void
}

DropDown.Item = function Item({ children, className }: DropDownItemProps) {
  const { setOpen } = useDropdownContext()

  return (
    <div
      onClick={() => {
        setOpen(false)
      }}
      className={clsx(className)}
    >
      {children}
    </div>
  )
}
