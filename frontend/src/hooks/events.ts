import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { EventCreateRequest } from '@/lib/api/gen.schemas'
import {
  createEventRouteEventsPost,
  getEventRouteEventsEventIdGet,
  getGroupEventsRouteEventsGroupsGroupIdGet,
} from '@/lib/api/events/events'
import {
  getPersonalGroupRouteUsersMeGroupsPersonalGet,
  listPersonalEventsRouteUsersMeEventsGet,
} from '@/lib/api/users/users'

export function usePersonalEvents() {
  return useQuery({
    queryKey: ['events', 'me'],
    queryFn: async () => {
      const [events, group] = await Promise.all([
        listPersonalEventsRouteUsersMeEventsGet(),
        getPersonalGroupRouteUsersMeGroupsPersonalGet(),
      ])

      return {
        ...group,
        events: events,
      }
    },
  })
}

export function useGroupEvents(groupId: number) {
  return useQuery({
    queryKey: ['events', 'groups', groupId],
    queryFn: () => getGroupEventsRouteEventsGroupsGroupIdGet(groupId),
  })
}

export function useEvent(id: number) {
  return useQuery({
    queryKey: ['events', id],
    queryFn: () => getEventRouteEventsEventIdGet(id),
  })
}

export function useCreateEvent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationKey: ['events'],
    mutationFn: (input: EventCreateRequest) =>
      createEventRouteEventsPost(input),
    onSuccess: async ({ groupId }) => {
      await queryClient.invalidateQueries({ queryKey: ['events', 'me'] })
      await queryClient.invalidateQueries({
        queryKey: ['events', 'groups', groupId],
      })
    },
  })
}
