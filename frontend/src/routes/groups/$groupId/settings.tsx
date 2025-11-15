import { createFileRoute, useNavigate, useParams } from '@tanstack/react-router'
import { Button, Flex, Input, Textarea, Typography } from '@maxhub/max-ui'
import { useState } from 'react'
import { useForm } from '@tanstack/react-form'
import { GroupPageLayout } from '@/components/layout/group-page-layout'
import { TimezoneInput } from '@/components/timezone-input'
import { useDeleteGroup, useEditGroup, useGroup } from '@/hooks/groups'
import { GroupTags } from '@/components/group/tag/group-tags'
import { TIMEZONES } from '@/constants'

export const Route = createFileRoute('/groups/$groupId/settings')({
  component: GroupSettingsPage,
})

function GroupSettingsPage() {
  const navigate = useNavigate()
  const { groupId } = useParams({ from: '/groups/$groupId/settings' })
  const groupQuery = useGroup(Number(groupId))
  const editGroupMutation = useEditGroup()
  const deleteGroupMutation = useDeleteGroup()
  const [isEditing, setIsEditing] = useState(false)

  const form = useForm({
    defaultValues: {
      name: groupQuery.data?.group.name || '',
      description: groupQuery.data?.group.description || '',
    },
    onSubmit: ({ value }) => {
      editGroupMutation.mutate(
        {
          groupId: Number(groupId),
          input: {
            name: value.name,
            description: value.description,
          },
        },
        { onSuccess: () => setIsEditing(false) },
      )
    },
  })

  return (
    <GroupPageLayout groupId={Number(groupId)}>
      <form
        id="edit-group"
        onSubmit={(e) => {
          e.preventDefault()
          form.handleSubmit()
        }}
        className="w-full h-full"
      >
        <Flex
          className="h-full pb-4 pt-2"
          direction="column"
          justify="space-between"
        >
          <Flex className="w-full" direction="column" gapY={22}>
            <form.Field
              name="name"
              children={(field) => (
                <Flex direction="column" className="w-full" gapY={12}>
                  <Typography.Title className="text-(--text-tertiary)">
                    Название
                  </Typography.Title>
                  <Input
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    disabled={!isEditing}
                    placeholder="Название"
                    mode="secondary"
                    className="w-full"
                    withClearButton={false}
                  />
                </Flex>
              )}
            />
            <form.Field
              name="description"
              children={(field) => (
                <Flex direction="column" className="w-full" gapY={12}>
                  <Typography.Title className="text-(--text-tertiary)">
                    Описание
                  </Typography.Title>
                  <Textarea
                    innerClassNames={{ textarea: 'min-h-24' }}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    disabled={!isEditing}
                    mode="secondary"
                    className="w-full"
                  />
                </Flex>
              )}
            />

            <Flex direction="column" className="w-full mt-5" gapY={12}>
              <Typography.Title className="text-(--text-tertiary)">
                Теги
              </Typography.Title>
              <GroupTags groupId={Number(groupId)} />
            </Flex>
          </Flex>

          <Flex className="self-end w-full" gapX={12}>
            {isEditing ? (
              <>
                <Button
                  form="edit-group"
                  key={'submit'}
                  type="submit"
                  className="grow"
                  mode="primary"
                >
                  Подтвердить
                </Button>
                <Button
                  onClick={() => {
                    form.reset()
                    setIsEditing(false)
                  }}
                  key={'cancel'}
                  type="button"
                  appearance="negative"
                  mode="secondary"
                >
                  Отменить
                </Button>
              </>
            ) : (
              <>
                <Button
                  key={'edit'}
                  type="button"
                  onClick={() => setIsEditing(true)}
                  className="grow"
                  mode="secondary"
                >
                  Изменить
                </Button>
                <Button
                  onClick={() => {
                    deleteGroupMutation.mutate(Number(groupId))
                    navigate({ to: '/' })
                  }}
                  key={'delete'}
                  type="button"
                  appearance="negative"
                  mode="secondary"
                >
                  Удалить
                </Button>
              </>
            )}
          </Flex>
        </Flex>
      </form>
    </GroupPageLayout>
  )
}
