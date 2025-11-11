import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMember } from './members'
import type {
  GroupCreateRequest,
  GroupUpdateRequest,
} from '@/lib/api/gen.schemas'
import {
  createGroupRouteGroupsPost,
  deleteGroupRouteGroupsGroupIdDelete,
  getGroupGroupsGroupIdGet,
  updateGroupRouteGroupsGroupIdPatch,
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
    queryFn: async () => getGroupGroupsGroupIdGet(groupId),
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

export function useMemberHasRole(groupId: number, rolesIds: Array<number>) {
  const { id } = useMaxUser()
  const { data } = useMember(groupId, id)
  return data && rolesIds.includes(data.member.role.id)
}

export function useEditGroup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationKey: ['groups'],
    mutationFn: ({
      groupId,
      input,
    }: {
      groupId: number
      input: GroupUpdateRequest
    }) => updateGroupRouteGroupsGroupIdPatch(groupId, input),
    onSuccess: async ({ group }) => {
      await queryClient.invalidateQueries({ queryKey: ['groups', group.id] })
    },
  })
}

export function useDeleteGroup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationKey: ['groups'],
    mutationFn: (groupId: number) =>
      deleteGroupRouteGroupsGroupIdDelete(groupId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}
