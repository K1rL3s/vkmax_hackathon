import { createFileRoute } from '@tanstack/react-router'
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
import { Bell, Clock3, Globe, Paperclip, RefreshCcw } from 'lucide-react'
import { useForm } from '@tanstack/react-form'
import type { TagResponse } from '@/lib/api/gen.schemas'
import { DynamicPageLayout } from '@/components/layout/dynamic-page-layout'
import { TimezoneInput } from '@/components/timezone-input'
import { TIMEZONES } from '@/components/timezone-select-modal'
import { TagsInput } from '@/components/member/tags-input'
import { RetryInput } from '@/components/retry-input'

export const Route = createFileRoute('/events/create')({
  component: CreateEventForm,
})

function CreateEventForm() {
  const form = useForm({
    defaultValues: {
      title: '',
      description: '',
      timezone: TIMEZONES[0],
      retry: {
        everyDay: false,
        everyWeek: false,
        everyMonth: false,
      },
      date: '',
      minutesBefore: 60,
      tagsIds: [] as Array<TagResponse>,
    },
    onSubmit: ({ value }) => {
      console.log(value)
    },
  })

  return (
    <DynamicPageLayout
      footer={
        <Container className="w-full pb-4">
          <div className="px-3">
            <Button form="create-event" type="submit" className="w-full">
              Создать
            </Button>
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
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                  )}
                />
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
                <form.Field
                  name="timezone"
                  children={(field) => (
                    <TimezoneInput
                      before={
                        <Globe
                          size={19}
                          color="currentColor"
                          className="text-(--icon-primary)"
                        />
                      }
                      value={field.state.value}
                      onChange={field.handleChange}
                    />
                  )}
                />
                <div className="border-b border-gray-200/10" />
                <Input
                  iconBefore={<Bell size={18} />}
                  placeholder="Напомнить за минут"
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
                      options={[
                        {
                          color: 'red',
                          groupId: 32,
                          name: '123',
                          id: 1,
                          description: '123',
                        },
                        {
                          color: 'green',
                          groupId: 32,
                          name: '123',
                          id: 2,
                          description: '123',
                        },
                      ]}
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
