import clsx from 'clsx'
import { CellList, CellSimple, Typography } from '@maxhub/max-ui'
import { ChevronDown } from 'lucide-react'
import { DropDown } from '../ui/dropdown'
import type { RoleResponse } from '@/lib/api/gen.schemas'

type RoleSelectProps = {
  value?: RoleResponse | undefined
  disabled?: boolean
  direction?: 'up' | 'down'
  variants: Array<RoleResponse>
  onChange: (role: RoleResponse) => void
}

export function RoleSelect({
  value,
  disabled,
  variants,
  direction = 'down',
  onChange,
}: RoleSelectProps) {
  const colorsStyles = {
    1: 'bg-amber-600',
    2: 'bg-blue-600',
    3: 'bg-green-600',
    4: 'bg-slate-500',
  }
  return (
    <DropDown>
      <DropDown.Trigger disabled={disabled}>
        <div
          className={clsx(
            'px-3 py-1.5 rounded-3xl flex items-center space-x-2',
            colorsStyles[value?.id as keyof typeof colorsStyles],
          )}
        >
          <Typography.Body>{value?.name}</Typography.Body>
          {!disabled && <ChevronDown size={16} />}
        </div>
      </DropDown.Trigger>
      <DropDown.Content
        className={clsx(
          'w-fit',
          { 'mt-2': direction === 'down', '-top-26': direction === 'up' },
          colorsStyles[value?.id as keyof typeof colorsStyles],
        )}
      >
        <CellList>
          {variants
            .filter((v) => v.id !== value?.id)
            .map((variant) => (
              <DropDown.Item key={variant.id}>
                <CellSimple
                  title={variant.name}
                  onClick={() => !disabled && onChange(variant)}
                  height="compact"
                />
              </DropDown.Item>
            ))}
        </CellList>
      </DropDown.Content>
    </DropDown>
  )
}
