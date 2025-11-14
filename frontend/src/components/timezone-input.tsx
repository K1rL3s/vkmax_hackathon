import { Flex } from '@maxhub/max-ui'
import clsx from 'clsx'
import React, { useState } from 'react'
import { TimezoneSelectModal } from './timezone-select-modal'

type Timezone = {
  label: string
  value: number
}

type TimezoneInputProps = {
  mode?: 'primary' | 'secondary'
  value?: Timezone | undefined
  disabled?: boolean
  onChange: (value: Timezone) => void
  header?: React.ReactNode
  before?: React.ReactNode
}

export function TimezoneInput({
  value,
  onChange,
  mode = 'primary',
  disabled = false,
  header,
  before,
}: TimezoneInputProps) {
  const [isSelecting, setIsSelecting] = useState(false)

  const modeStyles = {
    primary: 'bg-(--background-surface-card) text-(--text-secondary)',
    secondary:
      'bg-(--background-accent-neutral-fade-secondary) text-(--text-secondary)',
  }

  return (
    <>
      <Flex direction="column" gapY={12} className="w-full">
        {header}
        <button
          type="button"
          onClick={() => !disabled && setIsSelecting(true)}
          className={clsx(
            'min-h-[52px] w-full rounded-(--size-border-radius-semantic-border-radius-card) cursor-pointer text-start px-3',
            modeStyles[mode],
            {
              'bg-(--states-background-disabled-neutral-fade)!':
                disabled && mode === 'secondary',
            },
          )}
        >
          <Flex align="center" gapX={12}>
            {before}
            {value?.label}
          </Flex>
        </button>
      </Flex>
      <TimezoneSelectModal
        isOpen={isSelecting}
        onClose={() => setIsSelecting(false)}
        onSelect={onChange}
      />
    </>
  )
}
