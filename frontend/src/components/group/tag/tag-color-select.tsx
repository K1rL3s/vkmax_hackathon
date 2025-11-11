import { Flex, Typography } from '@maxhub/max-ui'

import clsx from 'clsx'

type Color = {
  className: string
  value: string
}

const TAG_COLORS: Array<Color> = [
  {
    className: 'bg-red-600',
    value: 'red',
  },
  {
    className: 'bg-green-600',
    value: 'green',
  },
  {
    className: 'bg-blue-600',
    value: 'blue',
  },
  {
    className: 'bg-yellow-600',
    value: 'yellow',
  },
  {
    className: 'bg-pink-600',
    value: 'pink',
  },
  {
    className: 'bg-orange-600',
    value: 'orange',
  },
  {
    className: 'bg-purple-600',
    value: 'purple',
  },
  {
    className: 'bg-cyan-600',
    value: 'cyan',
  },
]

type TagColorSelectProps = {
  value: string
  onChange: (c: string) => void
}

export function TagColorSelect({ value, onChange }: TagColorSelectProps) {
  return (
    <Flex className="w-full" direction="column" gapY={12}>
      <Typography.Title className="text-(--text-secondary)">
        Цвет
      </Typography.Title>
      <div className="p-3 rounded-2xl flex justify-start w-full bg-(--background-surface-card)">
        <Flex className="w-full space-x-4" wrap="wrap">
          {TAG_COLORS.map((c) => (
            <div
              onClick={() => onChange(c.value)}
              className={clsx(
                'size-10 rounded-full cursor-pointer mb-2',
                c.className,
                {
                  'ring-3 ring-(--accent-themed)': c.value === value,
                },
              )}
            />
          ))}
        </Flex>
      </div>
    </Flex>
  )
}
