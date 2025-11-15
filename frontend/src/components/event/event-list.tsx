import { Container, Flex, Typography } from '@maxhub/max-ui'
import { forwardRef, useImperativeHandle, useMemo, useRef } from 'react'
import { Devider } from '../ui/devider'
import { EventCard } from './event-card'

export type CalendarEvent = {
  id: number
  title: string
  date: Date
  type: 'message' | 'event'
}

export const EventList = forwardRef(function EventList(
  {
    events,
    onClick,
  }: {
    events: Array<CalendarEvent>
    onClick: (event: CalendarEvent) => void
  },
  ref,
) {
  const sectionsRef = useRef<Record<string, HTMLDivElement | null>>({})

  const schedule = useMemo(() => {
    const result: Record<
      string,
      | Array<{
          time: string
          event: CalendarEvent
        }>
      | undefined
    > = {
      [new Date().toISOString().split('T')[0]]: [],
    }

    for (const event of events) {
      const isoDate = event.date.toISOString().split('T')[0]
      const time = event.date.toLocaleTimeString('ru', {
        hour: '2-digit',
        minute: '2-digit',
      })

      result[isoDate] = result[isoDate] || []
      result[isoDate].push({ time, event: { ...event } })
    }

    return result
  }, [events])

  const today = new Date().toISOString().split('T')[0]

  const scrollToToday = () => {
    const section = sectionsRef.current[today]
    section?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  useImperativeHandle(ref, () => ({
    scrollToToday,
  }))

  return (
    <Flex className="w-full px-3" direction="column">
      {Object.entries(schedule)
        .sort(([a], [b]) => new Date(a).getTime() - new Date(b).getTime())
        .map(([date, times]) => {
          const formattedDate = new Date(date).toLocaleDateString('ru', {
            day: 'numeric',
            month: 'long',
          })
          const isToday = date === today

          return (
            <Flex
              className="w-full scroll-mt-20"
              key={date}
              direction="column"
              gapY={18}
              ref={(el) => {
                sectionsRef.current[date] = el
              }}
            >
              <Flex gapX={8} align="center">
                {isToday && (
                  <div className="bg-(--accent-themed) text-(--text-contrast-static) rounded-full pb-1 px-2">
                    <span className="text-xs">Сегодня</span>
                  </div>
                )}
                <Typography.Label className="font-bold">
                  {formattedDate}
                </Typography.Label>
              </Flex>

              {!times || times.length === 0 ? (
                <Container className="w-full h-16 text-center">
                  <Typography.Body className="text-sm">
                    Нет событий
                    <br />
                    Хорошего дня!
                  </Typography.Body>
                </Container>
              ) : (
                <Flex className="w-full" direction="column">
                  {times
                    .sort((a, b) => {
                      const [h1, m1] = a.time.split(':').map(Number)
                      const [h2, m2] = b.time.split(':').map(Number)
                      return h1 * 60 + m1 - (h2 * 60 + m2)
                    })
                    .map(({ time, event }) => (
                      <Container className="w-full" key={event.id}>
                        <Flex
                          align="flex-start"
                          gapX={12}
                          className="w-full"
                          key={event.id}
                        >
                          <Typography.Label className="font-semibold">
                            {time}
                          </Typography.Label>
                          <EventCard
                            key={event.id}
                            event={event}
                            onClick={() => onClick(event)}
                          />
                        </Flex>
                        <Devider />
                      </Container>
                    ))}
                </Flex>
              )}
            </Flex>
          )
        })}
    </Flex>
  )
})
