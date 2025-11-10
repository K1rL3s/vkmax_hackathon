import { Flex, Typography } from '@maxhub/max-ui'
import clsx from 'clsx'

type CardProps = React.ComponentProps<'div'>

export function Card({ children, ...props }: CardProps) {
  return (
    <Flex
      {...props}
      className={clsx(
        'rounded-(--size-border-radius-semantic-border-radius-card) bg-(--background-surface-card) w-full h-full',
        props.className,
      )}
      direction="column"
      gapY={12}
    >
      {children}
    </Flex>
  )
}

Card.Header = function CardHeader({ children }: { children: React.ReactNode }) {
  return <Typography.Title>{children}</Typography.Title>
}

Card.Content = function CardContent({
  children,
}: {
  children: React.ReactNode
}) {
  return <div className="w-full h-full">{children}</div>
}
