import { Flex, IconButton, Typography } from '@maxhub/max-ui'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Loader, PlusIcon, Search } from 'lucide-react'
import { useEffect, useRef } from 'react'
import { useEventsList } from '@/hooks/events'
import { Header } from '@/components/header'
import { EventList } from '@/components/event/event-list'
import { FloatingIconButton } from '@/components/ui/floating-button'

export const Route = createFileRoute('/')({
  component: Home,
})

function Home() {
  const { data, isPending } = useEventsList()
  const navigate = useNavigate()
  const scrollRef = useRef<{ scrollToToday: () => void }>(null)

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

  const today = new Date().getDate()
  return (
    <>
      <Flex direction="column" gapY={24}>
        <Header>
          <Flex gapX={8}>
            <IconButton mode="secondary" size="medium">
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
        <EventList events={data} ref={scrollRef} />
      </Flex>
      <FloatingIconButton onClick={() => navigate({ to: '/events/create' })}>
        <PlusIcon />
      </FloatingIconButton>
    </>
  )
}
