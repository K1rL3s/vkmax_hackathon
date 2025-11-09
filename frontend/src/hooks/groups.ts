import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { GroupCreateRequest } from '@/lib/api/gen.schemas'
import { useMaxUser } from '@/integrations/max-ui/hooks/max-user'
import { createGroupRouteGroupsPost } from '@/lib/api/groups/groups'
import { listUserGroupsRouteUsersUserIdGroupsGet } from '@/lib/api/users/users'

export function useGroups() {
  const { id } = useMaxUser()
  return useQuery({
    queryKey: ['groups'],
    queryFn: () =>
      listUserGroupsRouteUsersUserIdGroupsGet(id, { master_id: id }),
  })
}

export function useCreateGroup() {
  const { id } = useMaxUser()
  const queryClient = useQueryClient()
  return useMutation({
    mutationKey: ['groups'],
    mutationFn: (input: Omit<GroupCreateRequest, 'creatorId'>) =>
      createGroupRouteGroupsPost({ ...input, creatorId: id }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}
