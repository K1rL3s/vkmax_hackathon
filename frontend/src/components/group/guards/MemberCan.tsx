import { useMemberHasRole } from '@/hooks/groups'

export function MemberCan({
  children,
  rolesIds,
  groupId,
}: {
  children: React.ReactNode
  groupId: string
  rolesIds: Array<number>
}) {
  const hasPermission = useMemberHasRole(Number(groupId), rolesIds)
  return hasPermission ? <>{children}</> : null
}
