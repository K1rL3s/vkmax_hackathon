import clsx from 'clsx'
import { X } from 'lucide-react'
import { Typography } from '@maxhub/max-ui'
import type { TagResponse } from '@/lib/api/gen.schemas'

type TagProps = {
  tag: TagResponse
  onClick?: () => void
}

export function Tag({ tag, onClick }: TagProps) {
  const tagColorStyles = {
    red: 'bg-red-700',
    blue: 'bg-blue-700',
    green: 'bg-green-700',
    yellow: 'bg-yellow-700',
    purple: 'bg-purple-700',
    cyan: 'bg-cyan-700',
    pink: 'bg-pink-700',
    orange: 'bg-orange-700',
  }
  return (
    <div
      className={clsx(
        'rounded-full text-(--text-primary) flex items-center space-x-2 px-2 py-1 w-fit mr-2 my-1',
        tagColorStyles[tag.color as keyof typeof tagColorStyles],
      )}
    >
      <Typography.Body>{tag.name}</Typography.Body>
      {onClick && <X size={16} onClick={onClick} />}
    </div>
  )
}
