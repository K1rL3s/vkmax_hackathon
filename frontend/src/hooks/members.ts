import { useMaxUser } from '@/integrations/max-ui/hooks/max-user'
import type { GroupMemberUpdateRequest } from '@/lib/api/gen.schemas'
import {
  getGroupUserRouteGroupsGroupIdUsersMemberIdGet,
  listGroupUsersRouteGroupsGroupIdUsersGet,
  updateGroupMembershipGroupsGroupIdUsersSlaveIdPatch,
} from '@/lib/api/groups/groups'
import { listUserTagsRouteUsersUserIdGroupsGroupIdTagsGet } from '@/lib/api/users/users'
import { useMutation, useQuery } from '@tanstack/react-query'

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
  })
}
