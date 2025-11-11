import { Flex, Typography } from '@maxhub/max-ui'
import clsx from 'clsx'
import { useState } from 'react'
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
}

export function TimezoneInput({
  value,
  onChange,
  mode = 'primary',
  disabled = false,
}: TimezoneInputProps) {
  const [isSelecting, setIsSelecting] = useState(false)

  const modeStyles = {
    primary: 'bg-blue-500 text-white',
    secondary:
      'bg-(--background-accent-neutral-fade-secondary) text-(--text-secondary)',
  }

  return (
    <>
      <Flex direction="column" gapY={12} className="w-full">
        <Typography.Title className="text-(--text-tertiary)">
          Часовой пояс
        </Typography.Title>
        <button
          type="button"
          onClick={() => !disabled && setIsSelecting(true)}
          className={clsx(
            'min-h-[52px] w-full rounded-(--size-border-radius-semantic-border-radius-card) cursor-pointer text-start px-3',
            modeStyles[mode],
            { 'bg-(--states-background-disabled-neutral-fade)!': disabled },
          )}
        >
          {value?.label}
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
