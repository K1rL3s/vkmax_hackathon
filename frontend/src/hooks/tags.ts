import { useQuery } from '@tanstack/react-query'
import { listGroupTagsRouteGroupsGroupIdTagsGet } from '@/lib/api/tags/tags'

export function useGroupTags(groupId: number) {
  return useQuery({
    queryKey: ['tags', groupId],
    queryFn: () => listGroupTagsRouteGroupsGroupIdTagsGet(groupId),
  })
}
