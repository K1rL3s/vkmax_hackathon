import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/groups/$groupId/settings')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div></div>
}
