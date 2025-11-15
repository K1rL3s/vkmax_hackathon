import {
  CellList,
  Container,
  Flex,
  Grid,
  Input,
  Panel,
  Textarea,
  ToolButton,
  Typography,
} from '@maxhub/max-ui'
import { createFileRoute, useParams, useRouter } from '@tanstack/react-router'
import { Check, Clock, Edit2, Paperclip, Trash2Icon, X } from 'lucide-react'
import { useForm } from '@tanstack/react-form'
import z from 'zod'
import { useState } from 'react'
import type { TagResponse } from '@/lib/api/gen.schemas'
import { DynamicPageLayout } from '@/components/layout/dynamic-page-layout'
import { useDeleteEvent, useEditEvent, useEvent } from '@/hooks/events'
import { TagsInput } from '@/components/member/tags-input'
import { usePersonalGroupWithTags } from '@/hooks/groups'

export const Route = createFileRoute('/events/$id')({
  component: EventDetailsPage,
})

function EventDetailsPage() {
  const router = useRouter()
  const { id } = useParams({ from: '/events/$id' })
  const personalGroupQuery = usePersonalGroupWithTags()
  const eventQuery = useEvent(Number(id))
  const updateEventMutation = useEditEvent()
  const deleteEventMutation = useDeleteEvent()

  const [isEditing, setIsEditing] = useState(false)

  const form = useForm({
    defaultValues: {
      title: eventQuery.data?.title ?? '',
      description: eventQuery.data?.description ?? '',
      tagsIds: personalGroupQuery.data?.group.tags || [],
      duration: eventQuery.data?.duration ?? 60,
    },
    validators: {
      onChange: z.object({
        title: z.string().min(1, { error: 'Название не должно быть пустым' }),
        description: z.string(),
        duration: z.number().min(1),
        tagsIds: z.array(
          z.object({
            id: z.number(),
            name: z.string(),
            color: z.string(),
            groupId: z.number(),
          }),
        ),
      }),
    },
    onSubmit: ({ value }) => {
      updateEventMutation.mutate(
        {
          eventId: Number(id),
          input: {
            title: value.title,
            description: value.description,
            duration: value.duration,
            // до лучших времен
            // tagsIds: value.tagsIds.map((tag) => tag.id),
            // participantsIds: [personalGroupQuery.data!.id],
          },
        },
        {
          onSuccess: () => {
            setIsEditing(false)
          },
        },
      )
    },
  })

  return (
    <DynamicPageLayout
      footer={
        <Flex
          className="w-full py-1 px-3 bg-(--background-surface-card) rounded-t-4xl"
          gapX={12}
          justify="center"
        >
          <Grid cols={2} gapX={8}>
            {isEditing ? (
              <>
                <ToolButton
                  type="submit"
                  key={'submit'}
                  form="edit-event"
                  icon={<Check size={24} />}
                >
                  Применить
                </ToolButton>
                <ToolButton
                  onClick={() => {
                    form.reset()
                    setIsEditing(false)
                  }}
                  key={'cancel'}
                  icon={<X size={24} />}
                >
                  Отменить
                </ToolButton>
              </>
            ) : (
              <>
                <ToolButton
                  key={'edit'}
                  onClick={() => setIsEditing(true)}
                  icon={<Edit2 size={24} />}
                >
                  Изменить
                </ToolButton>
                <ToolButton
                  onClick={() => {
                    deleteEventMutation.mutate(Number(id))
                    router.history.back()
                  }}
                  key={'delete'}
                  icon={<Trash2Icon size={24} />}
                >
                  Удалить
                </ToolButton>
              </>
            )}
          </Grid>
        </Flex>
      }
      heading={<Typography.Headline>Просмотр события</Typography.Headline>}
    >
      <Panel className="w-full">
        <Container className="w-full">
          <Flex
            direction="column"
            justify="space-between"
            className="w-full h-full"
          >
            <form
              onSubmit={(e) => {
                e.preventDefault()
                e.stopPropagation()
                form.handleSubmit()
              }}
              id="edit-event"
              className="w-full h-full"
            >
              <CellList filled mode="island" className="*:overflow-visible!">
                <form.Field
                  name="title"
                  children={(field) => (
                    <Input
                      placeholder="Название"
                      value={field.state.value}
                      disabled={!isEditing}
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                  )}
                />
                <div className="border-b border-gray-200/10" />
                <form.Field
                  name="description"
                  children={(field) => (
                    <Textarea
                      className="min-h-25"
                      placeholder="Описание"
                      value={field.state.value}
                      disabled={!isEditing}
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                  )}
                />

                <div className="border-b border-gray-200/10" />
                <form.Field
                  name="duration"
                  children={(field) => (
                    <Input
                      className="w-full"
                      iconBefore={
                        <Flex align="center" gapX={10}>
                          <Clock size={18} />
                          <span className="text-nowrap text-(--text-secondary)">
                            Длится минут
                          </span>
                        </Flex>
                      }
                      withClearButton={false}
                      value={field.state.value}
                      disabled={!isEditing}
                      onChange={(e) => {
                        if (
                          isNaN(Number(e.target.value)) ||
                          Number(e.target.value) < 0
                        )
                          return
                        field.handleChange(Number(e.target.value))
                      }}
                    />
                  )}
                />
                <div className="border-b border-gray-200/10" />
                <form.Field
                  name="tagsIds"
                  children={(field) => (
                    <TagsInput
                      disabled={!isEditing}
                      fullWidth
                      onChange={(tag: TagResponse) => {
                        if (
                          field.state.value.map((t) => t.id).includes(tag.id)
                        ) {
                          field.handleChange(
                            field.state.value.filter((t) => t.id !== tag.id),
                          )
                        } else {
                          field.handleChange([...field.state.value, tag])
                        }
                      }}
                      value={field.state.value}
                      before={<Paperclip size={18} />}
                      options={personalGroupQuery.data?.group.tags || []}
                    />
                  )}
                />
              </CellList>
            </form>
          </Flex>
        </Container>
      </Panel>
    </DynamicPageLayout>
  )
}
