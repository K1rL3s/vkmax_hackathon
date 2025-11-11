import { useForm } from '@tanstack/react-form'
import { createFileRoute, useParams, useRouter } from '@tanstack/react-router'
import { z } from 'zod'
import { Button, Container, Flex, Input, Typography } from '@maxhub/max-ui'
import { DynamicPageLayout } from '@/components/layout/dynamic-page-layout'
import { TagColorSelect } from '@/components/group/tag/tag-color-select'
import { useCreateTag } from '@/hooks/tags'

export const Route = createFileRoute('/groups/$groupId/tags/create')({
  component: TagCreateFormPage,
})

function TagCreateFormPage() {
  const { groupId } = useParams({ from: '/groups/$groupId/tags/create' })
  const router = useRouter()
  const { mutate, isPending } = useCreateTag()

  const form = useForm({
    defaultValues: {
      name: '',
      color: 'red',
    },
    validators: {
      onChange: z.object({
        name: z.string().min(1, { error: 'Название обязательно' }),
        color: z.string().min(1, { error: 'Нужно выбрать цвет' }),
      }),
    },
    onSubmit: ({ value }) => {
      mutate(
        {
          groupId: Number(groupId),
          input: value,
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
        <Container className="mb-4">
          <Button
            form="create-tag"
            type="submit"
            mode="secondary"
            className="w-full mt-2"
            loading={isPending}
          >
            Создать
          </Button>
        </Container>
      }
    >
      <Container className="w-full h-full pb-10">
        <form
          id="create-tag"
          className="w-full h-full"
          onSubmit={(e) => {
            e.preventDefault()
            e.stopPropagation()
            form.handleSubmit()
          }}
        >
          <Flex
            className="w-full h-full"
            justify="space-between"
            direction="column"
            gapY={20}
          >
            <form.Field
              name="name"
              children={(field) => (
                <Flex className="w-full" direction="column" gapY={12}>
                  <Typography.Title className="text-(--text-secondary)">
                    Название
                  </Typography.Title>
                  <Input
                    className="w-full"
                    value={field.state.value}
                    placeholder="Название тега"
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                  <Typography.Body className="text-red-500" variant="medium">
                    {field.state.meta.errors
                      .map((err) => err?.message)
                      .join(',')}
                  </Typography.Body>
                </Flex>
              )}
            />
            <form.Field
              name="color"
              children={(field) => (
                <TagColorSelect
                  value={field.state.value}
                  onChange={field.handleChange}
                />
              )}
            />
          </Flex>
        </form>
      </Container>
    </DynamicPageLayout>
  )
}
