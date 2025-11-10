import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/groups/$id/settings')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div></div>
}
