import { Flex, IconButton, Typography } from '@maxhub/max-ui'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { PlusIcon, Search } from 'lucide-react'
import { useEffect, useRef } from 'react'
import { usePersonalEvents } from '@/hooks/events'
import { Header } from '@/components/header'
import { EventList } from '@/components/event/event-list'
import { FloatingIconButton } from '@/components/ui/floating-button'
import { FallbackLoader } from '@/components/ui/fallback-loader'
import { expandCronEvents } from '@/lib/utils/cron'

export const Route = createFileRoute('/')({
  component: Home,
})

function Home() {
  const { data, isPending } = usePersonalEvents()
  const navigate = useNavigate()
  const scrollRef = useRef<{ scrollToToday: () => void }>(null)

  const now = new Date()
  const start = new Date(now.getFullYear(), now.getMonth() - 2, now.getDate())
  const end = new Date(now.getFullYear(), now.getMonth() + 2, now.getDate())

  const formatted = data ? expandCronEvents(data.events, start, end) : []

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollToToday()
    }
  }, [data])

  const today = new Date().getDate()
  return (
    <>
      <Flex direction="column" gapY={24}>
        <Header>
          <Flex gapX={8}>
            <IconButton
              onClick={() => navigate({ to: '/search' })}
              mode="secondary"
              size="medium"
            >
              <Search size={16} />
            </IconButton>
            <IconButton
              onClick={() => scrollRef.current?.scrollToToday()}
              mode="secondary"
              size="medium"
            >
              <Typography.Title>{today}</Typography.Title>
            </IconButton>
          </Flex>
        </Header>
        <FallbackLoader isLoading={isPending || !data}>
          <EventList events={formatted} ref={scrollRef} />
        </FallbackLoader>
      </Flex>
      <FloatingIconButton
        onClick={() =>
          navigate({
            to: '/events/create',
            search: { groupId: String(data?.id) },
          })
        }
      >
        <PlusIcon />
      </FloatingIconButton>
    </>
  )
}
