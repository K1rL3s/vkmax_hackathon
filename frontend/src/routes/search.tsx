import {
  CellList,
  CellSimple,
  Container,
  Flex,
  Input,
  Panel,
  Typography,
} from '@maxhub/max-ui'
import { createFileRoute } from '@tanstack/react-router'
import { Calendar, Search } from 'lucide-react'
import { useMemo, useState } from 'react'
import type { CalendarEvent } from '@/components/event/event-list'
import { DynamicPageLayout } from '@/components/layout/dynamic-page-layout'
import { usePersonalGroupWithTags } from '@/hooks/groups'

import { TagsInput } from '@/components/member/tags-input'
import { usePersonalEvents } from '@/hooks/events'
import { expandCronEvents } from '@/lib/utils/cron'

export const Route = createFileRoute('/search')({
  component: SearchPersonalEventsPage,
})

function SearchPersonalEventsPage() {
  const groupQuery = usePersonalGroupWithTags()
  const eventsQuery = usePersonalEvents()
  const [query, setQuery] = useState('')

  const expanded = expandCronEvents(
    eventsQuery.data?.events || [],
    new Date(),
    new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
  )

  const calendar: { [date: string]: Array<CalendarEvent> | undefined } =
    useMemo(
      () =>
        expanded.reduce(
          (acc, event) => {
            const dateKey = event.date.toLocaleDateString('ru-RU', {
              weekday: 'short',
              day: '2-digit',
              month: 'short',
              year: 'numeric',
            })
            if (!acc[dateKey]) {
              acc[dateKey] = []
            }
            acc[dateKey].push(event)
            return acc
          },
          {} as { [date: string]: Array<CalendarEvent> | undefined },
        ),
      [expanded],
    )

  return (
    <DynamicPageLayout>
      <Panel className="w-full">
        <Container className="w-full h-full">
          <Flex gapY={22} direction="column" className="w-full h-full mb-4">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Поиск"
              iconBefore={<Search />}
              className="w-full"
            />
            <TagsInput
              className="px-0!"
              value={groupQuery.data?.group.tags}
              options={groupQuery.data?.group.tags}
            />
            <Flex className="w-full" gapY={38} direction="column">
              {Object.entries(calendar)
                .filter(
                  ([_, events]) =>
                    events?.filter((event) =>
                      event.title.toLowerCase().includes(query.toLowerCase()),
                    ).length,
                )
                .map(([date, events]) => (
                  <CellList
                    filled
                    mode="island"
                    className="w-full px-0!"
                    key={date}
                    header={
                      <div className="mb-3">
                        <Typography.Title>{date.slice(0, -8)}</Typography.Title>
                      </div>
                    }
                  >
                    {events?.map((event, index) => (
                      <>
                        <CellSimple
                          before={<Calendar size={18} />}
                          title={event.title}
                        />
                        {index !== events.length - 1 && (
                          <div className="h-px bg-gray-300/20" />
                        )}
                      </>
                    ))}
                  </CellList>
                ))}
            </Flex>
          </Flex>
        </Container>
      </Panel>
    </DynamicPageLayout>
  )
}
