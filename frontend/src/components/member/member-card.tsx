import { Avatar, CellSimple, Flex, Typography } from '@maxhub/max-ui'
import { useNavigate } from '@tanstack/react-router'
import clsx from 'clsx'
import type { GroupUserItem } from '@/lib/api/gen.schemas'

export function MemberCard({ member }: { member: GroupUserItem }) {
  const navigate = useNavigate()
  const isOwner = member.role.name.toLowerCase() === 'босс'

  return (
    <CellSimple
      onClick={() =>
        navigate({
          to: `/groups/${member.groupId}/members/${member.userId}`,
        })
      }
      key={member.maxId}
      before={
        <Avatar.Container>
          <Avatar.Text>
            {member.firstName?.charAt(0)}
            {member.lastName?.charAt(0)}
          </Avatar.Text>
        </Avatar.Container>
      }
      title={
        <Typography.Body>
          {member.firstName} {member.lastName}
        </Typography.Body>
      }
      after={
        <Flex gapX={10}>
          <span
            className={clsx('px-2 pb-1', {
              'text-(--text-themed)': isOwner,
            })}
          >
            <Typography.Label variant="large-caps">
              {member.role.name}
            </Typography.Label>
          </span>
        </Flex>
      }
    />
  )
}
