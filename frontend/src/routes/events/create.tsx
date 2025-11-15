import { createFileRoute, useRouter } from '@tanstack/react-router'
import {
  Button,
  CellList,
  Container,
  Flex,
  Input,
  Panel,
  Textarea,
  Typography,
} from '@maxhub/max-ui'
import { Bell, Clock, Clock3, Paperclip, RefreshCcw } from 'lucide-react'
import { useForm } from '@tanstack/react-form'
import { z } from 'zod'
import type { TagResponse } from '@/lib/api/gen.schemas'
import { DynamicPageLayout } from '@/components/layout/dynamic-page-layout'
import { TagsInput } from '@/components/member/tags-input'
import { RetryInput } from '@/components/retry-input'
import { usePersonalGroupWithTags } from '@/hooks/groups'
import { useCreateEvent } from '@/hooks/events'
import { toLocalDatetimeString } from '@/lib/utils/datetime'

export const Route = createFileRoute('/events/create')({
  component: CreateEventForm,
})

function CreateEventForm() {
  const router = useRouter()
  const personalGroupQuery = usePersonalGroupWithTags()
  const createEventMutation = useCreateEvent()
  const form = useForm({
    defaultValues: {
      title: '',
      description: '',

      retry: {
        everyDay: false,
        everyWeek: false,
        everyMonth: false,
      },
      date: toLocalDatetimeString(new Date()),
      minutesBefore: 60,
      tagsIds: personalGroupQuery.data?.group.tags || [],
      duration: 60,
    },
    validators: {
      onChange: z.object({
        title: z.string().min(1, { error: 'Название не должно быть пустым' }),
        description: z.string(),

        date: z.string().min(1, { error: 'Дата не должна быть пустой' }),
        minutesBefore: z
          .number()
          .min(1, { error: 'Значение должно быть не меньше 1' }),
        retry: z.object({
          everyDay: z.boolean(),
          everyWeek: z.boolean(),
          everyMonth: z.boolean(),
        }),
        tagsIds: z.array(
          z.object({
            id: z.number(),
            name: z.string(),
            color: z.string(),
            groupId: z.number(),
          }),
        ),
        duration: z
          .number()
          .min(1, { error: 'Значение должно быть не меньше 1' }),
      }),
    },
    onSubmit: ({ value }) => {
      createEventMutation.mutate(
        {
          title: value.title,
          description: value.description,
          cron: { date: value.date, ...value.retry },
          minutesBefore: [value.minutesBefore],
          tagsIds: value.tagsIds.map((tag) => tag.id),
          groupId: personalGroupQuery.data!.group.id,
          participantsIds: [personalGroupQuery.data!.id],
          duration: value.duration,
        },
        {
          onSuccess: () => {
            router.history.back()
          },
        },
      )
    },
  })

  return (
    <DynamicPageLayout
      footer={
        <Container className="w-full pb-4">
          <div className="px-3">
            <form.Subscribe
              selector={(state) => state.isFormValid && !state.isDefaultValue}
              children={(state) => (
                <Button
                  loading={createEventMutation.isPending}
                  form="create-event"
                  type="submit"
                  className="w-full"
                  disabled={!state}
                >
                  Создать
                </Button>
              )}
            />
          </div>
        </Container>
      }
      heading={<Typography.Headline>Создание события</Typography.Headline>}
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
              id="create-event"
              className="w-full h-full"
            >
              <CellList filled mode="island" className="*:overflow-visible!">
                <form.Field
                  name="title"
                  children={(field) => (
                    <Input
                      placeholder="Название"
                      value={field.state.value}
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
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                  )}
                />
                <div className="border-b border-gray-200/10" />
                <form.Field
                  name="date"
                  children={(field) => (
                    <Input
                      iconBefore={<Clock3 size={18} />}
                      step={-1}
                      type="datetime-local"
                      value={field.state.value}
                      onChange={(e) => {
                        field.handleChange(e.target.value)
                      }}
                    />
                  )}
                />
                <div className="border-b border-gray-200/10" />
                <form.Field
                  name="retry"
                  children={(field) => (
                    <RetryInput
                      before={
                        <RefreshCcw
                          size={18}
                          color="currentColor"
                          className="text-(--icon-primary)"
                        />
                      }
                      onChange={(retry) => field.handleChange(retry)}
                      value={field.state.value}
                    />
                  )}
                />

                <div className="border-b border-gray-200/10" />
                <form.Field
                  name="minutesBefore"
                  children={(field) => (
                    <Input
                      iconBefore={
                        <Flex align="center" gapX={10}>
                          <Bell size={18} />
                          <span className="text-nowrap text-(--text-secondary)">
                            Напомнить за
                          </span>
                        </Flex>
                      }
                      value={field.state.value}
                      onChange={(e) => {
                        if (isNaN(Number(e.target.value))) return
                        field.handleChange(Number(e.target.value))
                      }}
                      withClearButton={false}
                      placeholder="Напомнить за минут"
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
