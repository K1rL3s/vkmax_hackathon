import { Flex } from '@maxhub/max-ui'
import clsx from 'clsx'
import { useState } from 'react'
import type { GroupUserItem } from '@/lib/api/gen.schemas'

type ParticipantsInput = {
  value: Array<GroupUserItem>
  options: Array<GroupUserItem>
  onChange: (member: GroupUserItem) => void
  header?: React.ReactNode
  before?: React.ReactNode
  disabled?: boolean
  mode?: 'primary' | 'secondary'
}

export function ParticipantsInput({
  value,
  onChange,
  options,
  header,
  before,
  mode = 'primary',
  disabled = false,
}: ParticipantsInput) {
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
          )}
        >
          <Flex align="center" gapX={12}>
            {before}
            <flex></flex>
          </Flex>
        </button>
      </Flex>
    </>
  )
}
