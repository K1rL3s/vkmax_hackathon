import { listGroupTagsRouteGroupsGroupIdTagsGet } from '@/lib/api/tags/tags'
import { useQuery } from '@tanstack/react-query'

export function useGroupTags(groupId: number) {
  return useQuery({
    queryKey: ['tags', groupId],
    queryFn: () => listGroupTagsRouteGroupsGroupIdTagsGet(groupId),
  })
}
