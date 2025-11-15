import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type {
  EventCreateRequest,
  EventUpdateRequest,
} from '@/lib/api/gen.schemas'
import {
  createEventRouteEventsPost,
  deleteEventRouteEventsEventIdDelete,
  getEventRouteEventsEventIdGet,
  getGroupEventsRouteEventsGroupsGroupIdGet,
  updateEventRouteEventsEventIdPatch,
} from '@/lib/api/events/events'
import {
  getPersonalGroupRouteUsersMeGroupsPersonalGet,
  listPersonalEventsRouteUsersMeEventsGet,
} from '@/lib/api/users/users'

export function usePersonalEvents({
  tag_ids = [],
}: {
  tag_ids?: Array<string>
}) {
  return useQuery({
    queryKey: ['events', 'me', tag_ids.join(',')],
    queryFn: async () => {
      const [events, group] = await Promise.all([
        listPersonalEventsRouteUsersMeEventsGet({ tag_ids: tag_ids.join(',') }),
        getPersonalGroupRouteUsersMeGroupsPersonalGet(),
      ])

      return {
        ...group,
        events: events,
      }
    },
  })
}

export function useGroupEvents(
  groupId: number,
  { tag_ids = [] }: { tag_ids?: Array<string> },
) {
  return useQuery({
    queryKey: ['events', 'groups', groupId, tag_ids.join(',')],
    queryFn: () =>
      getGroupEventsRouteEventsGroupsGroupIdGet(groupId, {
        tag_ids: tag_ids.join(','),
      }),
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

export function useEditEvent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationKey: ['events', 'edit'],
    mutationFn: ({
      eventId,
      input,
    }: {
      eventId: number
      input: EventUpdateRequest
    }) => updateEventRouteEventsEventIdPatch(eventId, input),
    onSuccess: async ({ groupId, id }) => {
      await queryClient.invalidateQueries({ queryKey: ['events', 'me'] })
      await queryClient.invalidateQueries({
        queryKey: ['events', 'groups', groupId],
      })
      await queryClient.invalidateQueries({
        queryKey: ['events', id],
      })
    },
  })
}

export function useDeleteEvent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationKey: ['events', 'delete'],
    mutationFn: (eventId: number) => {
      return deleteEventRouteEventsEventIdDelete(eventId)
    },
    onSuccess: async (_) => {
      await queryClient.invalidateQueries({
        queryKey: ['events'],
      })
    },
  })
}
