import { Typography } from '@maxhub/max-ui'
import clsx from 'clsx'
import type { RoleResponse } from '@/lib/api/gen.schemas'

type RoleProps = {
  roleId: Pick<RoleResponse, 'id'>
}

export function Role({ roleId }: RoleProps) {
  const colorsStyles = {
    1: 'bg-amber-600',
    2: 'bg-blue-600',
    3: 'bg-green-600',
    4: 'bg-slate-500',
  }

  const roleNames = {
    3: 'Участник',
    2: 'Начальник',
    1: 'Босс',
  }

  return (
    <div
      className={clsx(
        'px-3 py-1.5 rounded-3xl flex items-center space-x-2',
        colorsStyles[roleId as unknown as keyof typeof colorsStyles],
      )}
    >
      <Typography.Body className="text-(--text-primary)">
        {roleNames[roleId as unknown as keyof typeof roleNames]}
      </Typography.Body>
    </div>
  )
}
