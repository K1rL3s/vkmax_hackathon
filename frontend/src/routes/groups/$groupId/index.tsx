import { useEffect, useRef } from 'react'
import { createFileRoute, useNavigate, useParams } from '@tanstack/react-router'
import { PlusIcon, Search } from 'lucide-react'
import { Flex, IconButton, Typography } from '@maxhub/max-ui'
import { EventList } from '@/components/event/event-list'
import { GroupPageLayout } from '@/components/layout/group-page-layout'
import { Loader } from '@/components/ui/loader'
import { useGroupEvents } from '@/hooks/events'
import { expandCronEvents } from '@/lib/utils/cron'
import { FloatingIconButton } from '@/components/ui/floating-button'

export const Route = createFileRoute('/groups/$groupId/')({
  component: GroupEventsPage,
})

function GroupEventsPage() {
  const { groupId } = useParams({ from: '/groups/$groupId/' })
  const { data, isPending } = useGroupEvents(Number(groupId))
  const scrollRef = useRef<{ scrollToToday: () => void }>(null)
  const navigate = useNavigate()

  const now = new Date()
  const start = new Date(now.getFullYear(), now.getMonth() - 2, now.getDate())
  const end = new Date(now.getFullYear(), now.getMonth() + 2, now.getDate())

  const formatted = data?.events
    ? expandCronEvents(data.events, start, end)
    : []

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollToToday()
    }
  }, [data])

  if (isPending || !data) {
    return (
      <div className="mt-12 w-full h-full">
        <Loader size={38} />
      </div>
    )
  }

  return (
    <GroupPageLayout
      className="h-full!"
      groupId={Number(groupId)}
      heading={
        <Flex gapX={8}>
          <IconButton mode="secondary" size="medium">
            <Search size={16} />
          </IconButton>
          <IconButton
            onClick={() => scrollRef.current?.scrollToToday()}
            mode="secondary"
            size="medium"
          >
            <Typography.Title>{now.getDate()}</Typography.Title>
          </IconButton>
        </Flex>
      }
    >
      <EventList events={formatted} ref={scrollRef} />

      <FloatingIconButton
        onClick={() =>
          navigate({
            to: '/groups/$groupId/events/create',
            params: { groupId: groupId },
          })
        }
      >
        <PlusIcon />
      </FloatingIconButton>
    </GroupPageLayout>
  )
}
