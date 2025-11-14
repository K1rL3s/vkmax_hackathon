import { Flex, Typography } from '@maxhub/max-ui'
import clsx from 'clsx'
import React, { useState } from 'react'
import { Modal } from './ui/modal'
import { RatioInput } from './ui/ratio-input'
import type { Option } from './ui/ratio-input'

type Retry = {
  everyWeek: boolean
  everyDay: boolean
  everyMonth: boolean
}

type RetryInputProps = {
  mode?: 'primary' | 'secondary'
  value?: Retry | undefined
  disabled?: boolean
  onChange: (value: Retry) => void
  header?: React.ReactNode
  before?: React.ReactNode
}

export function RetryInput({
  value,
  onChange,
  mode = 'primary',
  disabled = false,
  header,
  before,
}: RetryInputProps) {
  const [isSelecting, setIsSelecting] = useState(false)

  const modeStyles = {
    primary: 'bg-(--background-surface-card) text-(--text-secondary)',
    secondary:
      'bg-(--background-accent-neutral-fade-secondary) text-(--text-secondary)',
  }

  const label = () => {
    if (!value || Object.values(value).every((v) => !v)) return 'Не повторять'
    if (value.everyDay) return 'Каждый день'
    if (value.everyWeek) return 'Каждую неделю'
    if (value.everyMonth) return 'Каждый месяц'
  }

  const handleChange = (option: Option) => {
    const map: Record<number, keyof Retry> = {
      1: 'everyDay',
      2: 'everyWeek',
      3: 'everyMonth',
    }

    if (option.id === 0) {
      onChange({
        everyWeek: false,
        everyDay: false,
        everyMonth: false,
      })
      return setIsSelecting(false)
    }

    const res: Retry = {
      everyWeek: false,
      everyDay: false,
      everyMonth: false,
    }

    const key = map[option.id]
    res[key] = true

    onChange(res)
    setIsSelecting(false)
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
            {
              'bg-(--states-text-disabled-primary)! text(--states-text-disabled-primary)':
                disabled && mode === 'secondary',
            },
          )}
        >
          <Flex align="center" gapX={12}>
            {before}
            {label()}
          </Flex>
        </button>
      </Flex>
      <Modal
        className="w-full"
        isOpen={isSelecting}
        onClose={() => setIsSelecting(false)}
      >
        <div className="py-1">
          <RatioInput
            header={
              <Typography.Headline variant="medium">
                Повторять
              </Typography.Headline>
            }
            value={(() => {
              if (!value) return 0
              if (value.everyDay) return 1
              if (value.everyWeek) return 2
              if (value.everyMonth) return 3
              return 0
            })()}
            onChange={handleChange}
            options={[
              { id: 0, label: 'Не повторять' },
              { id: 1, label: 'Каждый день' },
              { id: 2, label: 'Каждую неделю' },
              { id: 3, label: 'Каждый месяц' },
            ]}
          />
        </div>
      </Modal>
    </>
  )
}
