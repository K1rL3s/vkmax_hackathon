import { Card } from '@/components/card'
import { GroupPageLayout } from '@/components/layout/group-page-layout'
import { MemberCard } from '@/components/member-card'

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

export const Route = createFileRoute('/groups/$id/members')({
  component: RouteComponent,
})

function RouteComponent() {
  const { id } = useParams({ from: '/groups/$id/members' })
  const { data, isPending } = useMembers(Number(id))
  const [query, setQuery] = useState('')

  const members = data?.filter(
    (member) =>
      member.firstName.toLowerCase().includes(query.toLowerCase()) ||
      member?.lastName?.toLowerCase().includes(query.toLowerCase()),
  )

  return (
    <GroupPageLayout groupId={Number(id)}>
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
            <CellList className="max-h-0" mode="full-width">
              {members?.map((member) => (
                <>
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                  <MemberCard key={member.maxId} member={member} />
                </>
              ))}
            </CellList>
          )}
        </Card>
        <Card className="w-full h-fit! px-4 py-2 mb-4">
          <Card.Content>
            <Flex className="w-full" align="center" justify="space-between">
              <select>
                <option>Пользователь</option>
                <option>Администратор</option>
              </select>
              <Button
                iconBefore={<Link size={18} />}
                appearance="themed"
                className="flex items-center"
              >
                <Typography.Body>Пригласить</Typography.Body>
              </Button>
            </Flex>
          </Card.Content>
        </Card>
      </Flex>
    </GroupPageLayout>
  )
}
