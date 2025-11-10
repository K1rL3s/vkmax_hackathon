import type { GroupUserItem } from '@/lib/api/gen.schemas'
import { Avatar, Button, CellSimple, Flex, Typography } from '@maxhub/max-ui'
import clsx from 'clsx'

export function MemberCard({ member }: { member: GroupUserItem }) {
  const isOwner = member.roleName.toLowerCase() === 'босс'
  return (
    <CellSimple
      onClick={() => {}}
      key={member.maxId}
      before={
        <Avatar.Container>
          <Avatar.Text>
            {member.firstName.charAt(0)}
            {member?.lastName?.charAt(0)}
          </Avatar.Text>
        </Avatar.Container>
      }
      title={
        <Typography.Body>
          {member.firstName} {member?.lastName}
        </Typography.Body>
      }
      after={
        <Flex gapX={22}>
          {isOwner ? (
            <select
              className="
    appearance-none
            w-full
            rounded-xl
            border border-gray-200 dark:border-gray-700
            bg-white dark:bg-gray-800
            text-gray-900 dark:text-gray-100
            px-3 py-2 pr-8
            text-sm
            focus:outline-none
            focus:ring-2 focus:ring-primary-500
            hover:bg-gray-50 dark:hover:bg-gray-700
            transition
            cursor-pointer
  "
              defaultValue={member.roleName.toLocaleLowerCase()}
            >
              <option value={2}>Начальник</option>
              <option value={1}>Участник</option>
            </select>
          ) : (
            <span
              className={clsx('px-2 pb-1', {
                'text-(--text-themed)':
                  member.roleName.toLocaleLowerCase() === 'босс',
              })}
            >
              <Typography.Label variant="large-caps">
                {member.roleName}
              </Typography.Label>
            </span>
          )}

          {isOwner && (
            <Button
              appearance="negative"
              mode="secondary"
              size="small"
              className="text-(--text-muted)"
            >
              Исключить
            </Button>
          )}
        </Flex>
      }
    />
  )
}
