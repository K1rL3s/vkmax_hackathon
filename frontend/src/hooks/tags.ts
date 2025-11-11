import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { TagCreateRequest } from '@/lib/api/gen.schemas'
import {
  createTagRouteGroupsGroupIdTagsPost,
  deleteTagRouteGroupsGroupIdTagsTagIdDelete,
  listGroupTagsRouteGroupsGroupIdTagsGet,
} from '@/lib/api/tags/tags'

export function useGroupTags(groupId: number) {
  return useQuery({
    queryKey: ['tags', groupId],
    queryFn: () => listGroupTagsRouteGroupsGroupIdTagsGet(groupId),
  })
}

export function useCreateTag() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationKey: ['tags', 'create'],
    mutationFn: ({
      groupId,
      input,
    }: {
      groupId: number
      input: TagCreateRequest
    }) => createTagRouteGroupsGroupIdTagsPost(groupId, input),
    onSuccess: async ({ groupId }) => {
      await queryClient.invalidateQueries({ queryKey: ['tags', groupId] })
    },
  })
}

export function useDeleteTags() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationKey: ['tags', 'delete'],
    mutationFn: ({ groupId, tagId }: { groupId: number; tagId: number }) =>
      deleteTagRouteGroupsGroupIdTagsTagIdDelete(groupId, tagId),
    onSuccess: async (_, { groupId }) => {
      await queryClient.invalidateQueries({ queryKey: ['tags', groupId] })
    },
  })
}
