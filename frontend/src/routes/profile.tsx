import { Flex } from '@maxhub/max-ui'
import { createFileRoute } from '@tanstack/react-router'
import { Header } from '@/components/header'

export const Route = createFileRoute('/profile')({
  component: ProfilePage,
})

function ProfilePage() {
  return (
    <Flex direction="column" gapY={24}>
      <Header />
    </Flex>
  )
}
