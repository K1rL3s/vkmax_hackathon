import { useMaxUser } from '@/integrations/max-ui/hooks/max-user'
import { listGroupUsersRouteGroupsGroupIdUsersGet } from '@/lib/api/groups/groups'
import { useQuery } from '@tanstack/react-query'

export function useMembers(groupId: number) {
  const { id } = useMaxUser()
  return useQuery({
    queryKey: ['members', groupId],
    queryFn: () =>
      listGroupUsersRouteGroupsGroupIdUsersGet(groupId, { user_id: id }),
  })
}
