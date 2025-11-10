import { Card } from '@/components/card'
import { GroupPageLayout } from '@/components/layout/group-page-layout'
import { MemberCard } from '@/components/member/member-card'
import { MemberInvite } from '@/components/member/member-invite'
import { RoleSelect } from '@/components/member/role-select'

import { useMembers } from '@/hooks/members'
import {
  Button,
  CellList,
  Flex,
  Input,
  Spinner,
  Typography,
} from '@maxhub/max-ui'
import { createFileRoute, useParams } from '@tanstack/react-router'
import { Link, SearchIcon } from 'lucide-react'
import { useState } from 'react'

export const Route = createFileRoute('/groups/$groupId/members/')({
  component: RouteComponent,
})

function RouteComponent() {
  const { groupId } = useParams({ from: '/groups/$groupId/members/' })
  const { data, isPending } = useMembers(Number(groupId))
  const [query, setQuery] = useState('')

  const members = data?.filter(
    (member) =>
      member?.firstName?.toLowerCase().includes(query.toLowerCase()) ||
      member?.lastName?.toLowerCase().includes(query.toLowerCase()),
  )

  return (
    <GroupPageLayout groupId={Number(groupId)}>
      <Flex className="h-full" direction="column" gapY={16}>
        <Input
          className="w-full shrink-0"
          placeholder="Поиск"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          iconBefore={<SearchIcon size={18} />}
        />
        <Card className="overflow-y-auto">
          {isPending ? (
            <div className="w-full h-full flex items-center justify-center">
              <Spinner />
            </div>
          ) : (
            <>
              {members?.length == 0 && (
                <div className="w-full h-full flex items-center justify-center mt-5">
                  <Typography.Body>Нет участников</Typography.Body>
                </div>
              )}
              <CellList className="max-h-0" mode="full-width">
                {members?.map((member) => (
                  <MemberCard key={member.maxId} member={member} />
                ))}
              </CellList>
            </>
          )}
        </Card>
        <MemberInvite groupId={groupId} />
      </Flex>
    </GroupPageLayout>
  )
}
