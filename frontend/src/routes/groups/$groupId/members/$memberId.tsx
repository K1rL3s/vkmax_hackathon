import {
  Container,
  Flex,
  Grid,
  Panel,
  Spinner,
  ToolButton,
  Typography,
} from '@maxhub/max-ui'
import { useForm } from '@tanstack/react-form'
import { createFileRoute, useNavigate, useParams } from '@tanstack/react-router'
import { Check, Edit2, X } from 'lucide-react'
import { useState } from 'react'
import { Avatar } from '@/components/avatar'
import { MemberCan } from '@/components/group/guards/MemberCan'
import { DynamicPageLayout } from '@/components/layout/dynamic-page-layout'
import { RoleSelect } from '@/components/member/role-select'
import { TagsInput } from '@/components/member/tags-input'
import { useMemberHasRole } from '@/hooks/groups'
import { useEditMember, useMember, useRemoveMember } from '@/hooks/members'
import { useGroupTags } from '@/hooks/tags'

export const Route = createFileRoute('/groups/$groupId/members/$memberId')({
  component: MemberPage,
})

function MemberPage() {
  const { groupId, memberId } = useParams({
    from: '/groups/$groupId/members/$memberId',
  })
  const navigate = useNavigate()
  const canEditRole = useMemberHasRole(Number(groupId), [1])
  const canEditTags = useMemberHasRole(Number(groupId), [1, 2])
  const memberQuery = useMember(Number(groupId), Number(memberId))
  const memberMutation = useEditMember()
  const kickMemberMutation = useRemoveMember()
  const groupTagsQuery = useGroupTags(Number(groupId))
  const [isEditing, setIsEditing] = useState(false)

  const handleKick = () => {
    kickMemberMutation.mutate(
      {
        groupId: Number(groupId),
        memberId: Number(memberId),
      },
      {
        onSuccess: () => {
          navigate({ to: `/groups/${groupId}/members` })
        },
      },
    )
  }

  const form = useForm({
    defaultValues: {
      role: memberQuery.data?.member.role,
      tags: memberQuery.data?.tags ?? [],
    },
    onSubmit: ({ value }) => {
      setIsEditing(false)
      memberMutation.mutate({
        groupId: Number(groupId),
        memberId: Number(memberId),
        input: {
          roleId: value.role?.id,
          tags: value.tags.map((tag) => tag.id),
        },
      })
    },
  })

  return (
    <DynamicPageLayout
      footer={
        <MemberCan groupId={groupId} rolesIds={[1, 2]}>
          <Flex
            className="w-full py-1 px-3 bg-(--background-surface-card) rounded-t-4xl"
            gapX={12}
            justify="center"
          >
            <Grid cols={2} gapX={8}>
              {!isEditing ? (
                <>
                  <ToolButton
                    onClick={() => setIsEditing(true)}
                    icon={<Edit2 size={24} />}
                  >
                    Изменить
                  </ToolButton>
                  <ToolButton onClick={handleKick} icon={<X size={24} />}>
                    Исключить
                  </ToolButton>
                </>
              ) : (
                <>
                  <ToolButton
                    onClick={() => form.handleSubmit()}
                    icon={<Check size={24} />}
                  >
                    Подтвердить
                  </ToolButton>
                  <ToolButton
                    onClick={() => {
                      form.reset()
                      setIsEditing(false)
                    }}
                    icon={<X size={24} />}
                  >
                    Отмена
                  </ToolButton>
                </>
              )}
            </Grid>
          </Flex>
        </MemberCan>
      }
    >
      {memberQuery.isPending ? (
        <div className="w-full h-full flex item-center justify-center">
          <Spinner />
        </div>
      ) : (
        <Panel>
          <form>
            <Flex direction="column" gapY={24}>
              <Container className="w-full">
                <Flex direction="column" gapY={16} align="center">
                  <Avatar
                    size={72}
                    firstName={memberQuery.data?.member.firstName?.toString()}
                    lastName={memberQuery.data?.member.lastName?.toString()}
                  />
                  <Typography.Headline variant="large-strong">
                    {memberQuery.data?.member.firstName}{' '}
                    {memberQuery.data?.member.lastName}
                  </Typography.Headline>
                  <form.Field
                    name="role"
                    children={(field) => (
                      <RoleSelect
                        value={field.state.value}
                        onChange={(val) => field.handleChange(val)}
                        disabled={!isEditing || !canEditRole}
                        variants={[
                          { id: 2, name: 'Начальник' },
                          { id: 3, name: 'Участник' },
                        ]}
                      />
                    )}
                  />
                </Flex>
              </Container>
              <form.Field
                name="tags"
                children={(field) => (
                  <TagsInput
                    value={field.state.value}
                    options={groupTagsQuery.data}
                    onChange={(tag) => {
                      const exists = field.state.value.some(
                        (t) => t.id === tag.id,
                      )
                      const newTags = exists
                        ? field.state.value.filter((t) => t.id !== tag.id)
                        : [...field.state.value, tag]
                      field.handleChange(newTags)
                    }}
                    disabled={!isEditing || !canEditTags}
                  />
                )}
              />
            </Flex>
          </form>
        </Panel>
      )}
    </DynamicPageLayout>
  )
}
