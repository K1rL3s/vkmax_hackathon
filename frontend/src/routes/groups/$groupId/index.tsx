import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/groups/$groupId/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/groups/$id/"!</div>
}
