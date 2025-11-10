import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { GroupCreateRequest } from '@/lib/api/gen.schemas'
import {
  createGroupRouteGroupsPost,
  getGroupGroupsGroupIdGet,
} from '@/lib/api/groups/groups'
import { listUserGroupsRouteUsersUserIdGroupsGet } from '@/lib/api/users/users'
import { useMaxUser } from '@/integrations/max-ui/hooks/max-user'

export function useGroups() {
  const { id } = useMaxUser()
  return useQuery({
    queryKey: ['groups'],
    queryFn: () => listUserGroupsRouteUsersUserIdGroupsGet(id),
  })
}

export function useGroup(groupId: number) {
  return useQuery({
    queryKey: ['groups', groupId],
    queryFn: () => getGroupGroupsGroupIdGet(groupId),
  })
}

export function useCreateGroup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationKey: ['groups'],
    mutationFn: (input: GroupCreateRequest) =>
      createGroupRouteGroupsPost(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}
