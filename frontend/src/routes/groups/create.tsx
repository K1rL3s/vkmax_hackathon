import {
  Button,
  Container,
  Flex,
  Input,
  Textarea,
  Typography,
} from '@maxhub/max-ui'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useForm } from '@tanstack/react-form'
import { z } from 'zod'
import { Header } from '@/components/header'
import { useCreateGroup } from '@/hooks/groups'

export const Route = createFileRoute('/groups/create')({
  component: CreateGroupFormPage,
})

function CreateGroupFormPage() {
  const { mutate, isPending } = useCreateGroup()
  const navigate = useNavigate()
  const form = useForm({
    defaultValues: {
      name: '',
      description: '',
    },
    validators: {
      onChange: z.object({
        name: z
          .string()
          .min(1, { message: 'Имя группы обязательно' })
          .max(100, { message: 'Имя группы не может превышать 100 символов' }),
        description: z.string().max(500, {
          message: 'Описание группы не может превышать 500 символов',
        }),
      }),
    },
    onSubmit: ({ value }) => {
      mutate(value, {
        onSuccess: ({ id }) => {
          navigate({ to: '/groups/$id', params: { id: id.toString() } })
        },
      })
    },
  })

  return (
    <Flex direction="column" className="h-screen" gapY={24}>
      <Header />
      <Container className="w-full h-full pb-10">
        <form
          id="create-group"
          className="w-full h-full"
          onSubmit={(e) => {
            e.preventDefault()
            e.stopPropagation()
            form.handleSubmit()
          }}
        >
          <Flex direction="column" className="h-full" justify="space-between">
            <Flex direction="column" gapY={18} className="w-full">
              <form.Field
                name="name"
                children={(field) => (
                  <>
                    <Input
                      name={field.name}
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      placeholder="Название"
                      mode="secondary"
                      className="w-full"
                    />
                    {!field.state.meta.isValid && (
                      <Typography.Body className="text-(--accent-red)">
                        {field.state.meta.errors
                          .map((err) => err?.message)
                          .join(',')}
                      </Typography.Body>
                    )}
                  </>
                )}
              />
              <form.Field
                name="description"
                children={(field) => (
                  <>
                    <Textarea
                      innerClassNames={{ textarea: 'min-h-24' }}
                      placeholder="Описание"
                      mode="secondary"
                      className="w-full"
                    />
                    {!field.state.meta.isValid && (
                      <em>
                        {field.state.meta.errors
                          .map((err) => err?.message)
                          .join(',')}
                      </em>
                    )}
                  </>
                )}
              />
            </Flex>
            <Button
              form="create-group"
              type="submit"
              size="large"
              className="w-full"
              loading={isPending}
            >
              Создать
            </Button>
          </Flex>
        </form>
      </Container>
    </Flex>
  )
}
