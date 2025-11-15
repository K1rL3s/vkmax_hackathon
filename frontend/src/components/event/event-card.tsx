import { Container, Flex, Typography } from '@maxhub/max-ui'
import { CalendarIcon, MessageCircleMoreIcon } from 'lucide-react'
import type { CalendarEvent } from './event-list'

export function EventCard({
  event,
  onClick,
}: {
  event: CalendarEvent
  onClick: () => void
}) {
  const beforeIcon = {
    event: <CalendarIcon size={18} />,
    message: <MessageCircleMoreIcon size={18} />,
  }[event.type]

  return (
    <div className="cursor-pointer" onClick={onClick}>
      <Container className="w-full bg-(--accent-themed)/70 text-(--text-contrast-static) rounded-xl py-2">
        <Flex align="center" gapX={8}>
          {beforeIcon}
          <Flex direction="column" gapY={6}>
            <Typography.Title>{event.title}</Typography.Title>
          </Flex>
        </Flex>
      </Container>
    </div>
  )
}
