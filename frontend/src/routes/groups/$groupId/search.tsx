import {
  CellList,
  CellSimple,
  Flex,
  Input,
  Panel,
  Typography,
  Container,
} from '@maxhub/max-ui'
import { createFileRoute, useNavigate, useParams } from '@tanstack/react-router'
import { Calendar, Search } from 'lucide-react'
import { useMemo, useState } from 'react'
import type { CalendarEvent } from '@/components/event/event-list'
import type { TagResponse } from '@/lib/api/gen.schemas'
import { TagsInput } from '@/components/member/tags-input'
import { useGroupEvents, usePersonalEvents } from '@/hooks/events'
import { useGroupWithTags, usePersonalGroupWithTags } from '@/hooks/groups'
import { expandCronEvents } from '@/lib/utils/cron'
import { DynamicPageLayout } from '@/components/layout/dynamic-page-layout'

export const Route = createFileRoute('/groups/$groupId/search')({
  component: SearchPersonalEventsPage,
})

function SearchPersonalEventsPage() {
  const [selectedTags, setSelectedTags] = useState<Array<TagResponse>>([])
  const { groupId } = useParams({ from: '/groups/$groupId/search' })
  const groupQuery = useGroupWithTags(Number(groupId))
  const navigate = useNavigate()
  const eventsQuery = useGroupEvents(Number(groupId), {
    tag_ids: selectedTags.map((tag) => tag.id.toString()),
  })
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
    <DynamicPageLayout
      heading={
        <Typography.Headline>{groupQuery.data?.group.name}</Typography.Headline>
      }
    >
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
              value={selectedTags}
              options={groupQuery.data?.group.tags}
              onChange={(tag) => {
                if (selectedTags.map((t) => t.id).includes(tag.id)) {
                  setSelectedTags(selectedTags.filter((t) => t.id !== tag.id))
                } else {
                  setSelectedTags([...selectedTags, tag])
                }
              }}
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
                          onClick={() =>
                            navigate({
                              to: '/events/$id',
                              params: { id: String(event.id) },
                            })
                          }
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
