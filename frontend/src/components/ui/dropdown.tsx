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
    throw new Error('useDropdownContext must be used within a DropdownProvider')
  }
  return ctx
}

type DropDownProps = {
  children: React.ReactNode
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
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  return (
    <DropdownContext.Provider value={{ open, setOpen }}>
      <div className={clsx('relative inline-block', className)} ref={ref}>
        {children}
      </div>
    </DropdownContext.Provider>
  )
}

type DropDownTriggerProps = {
  children: React.ReactNode
  className?: string
}

DropDown.Trigger = function Trigger({
  children,
  className,
}: DropDownTriggerProps) {
  const { open, setOpen } = useDropdownContext()
  return (
    <div onClick={() => setOpen(!open)} className={clsx(className)}>
      {children}
    </div>
  )
}

type DropDownContentProps = {
  children: React.ReactNode
  className?: string
}

DropDown.Content = function Content({
  children,
  className,
}: DropDownContentProps) {
  return (
    <div className={clsx('absolute z-10 mt-2 w-full rounded-(--)', className)}>
      {children}
    </div>
  )
}
