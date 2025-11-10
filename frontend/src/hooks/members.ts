import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { GroupMemberUpdateRequest } from '@/lib/api/gen.schemas'
import { useMaxUser } from '@/integrations/max-ui/hooks/max-user'
import {
  getGroupUserRouteGroupsGroupIdUsersMemberIdGet,
  listGroupUsersRouteGroupsGroupIdUsersGet,
  removeGroupMemberRouteGroupsGroupIdUsersSlaveIdDelete,
  updateGroupMembershipGroupsGroupIdUsersSlaveIdPatch,
} from '@/lib/api/groups/groups'
import { listUserTagsRouteUsersUserIdGroupsGroupIdTagsGet } from '@/lib/api/users/users'

export function useMembers(groupId: number) {
  const { id } = useMaxUser()
  return useQuery({
    queryKey: ['members', groupId],
    queryFn: () =>
      listGroupUsersRouteGroupsGroupIdUsersGet(groupId, { user_id: id }),
  })
}

export function useMember(groupId: number, memberId: number) {
  return useQuery({
    queryKey: ['members', groupId, memberId],
    queryFn: async () => {
      const [member, tags] = await Promise.all([
        getGroupUserRouteGroupsGroupIdUsersMemberIdGet(groupId, memberId),
        listUserTagsRouteUsersUserIdGroupsGroupIdTagsGet(memberId, groupId),
      ])
      return { member, tags }
    },
  })
}

export function useEditMember() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationKey: ['members', 'edit'],
    mutationFn: ({
      groupId,
      memberId,
      input,
    }: {
      groupId: number
      memberId: number
      input: GroupMemberUpdateRequest
    }) =>
      updateGroupMembershipGroupsGroupIdUsersSlaveIdPatch(
        groupId,
        memberId,
        input,
      ),
    onSuccess: async ({ groupId }) => {
      await queryClient.invalidateQueries({ queryKey: ['members', groupId] })
    },
  })
}

export function useRemoveMember() {
  return useMutation({
    mutationKey: ['members', 'remove'],
    mutationFn: ({
      groupId,
      memberId,
    }: {
      groupId: number
      memberId: number
    }) =>
      removeGroupMemberRouteGroupsGroupIdUsersSlaveIdDelete(groupId, memberId),
  })
}
