import { useForm } from '@tanstack/react-form'
import { Button, Flex, Input, Typography } from '@maxhub/max-ui'
import { z } from 'zod'
import { TagColorSelect } from './tag-color-select'
import type { TagCreateRequest } from '@/lib/api/gen.schemas'

type TagCreateForm = {
  onCreate?: (input: TagCreateRequest) => void | undefined
}

export function TagCreateForm({ onCreate }: TagCreateForm) {
  const form = useForm({
    defaultValues: {
      name: '',
      color: 'red',
    },
    validators: {
      onSubmit: z.object({
        name: z.string().min(1, { error: 'Название обязательно' }),
        color: z.string().min(1, { error: 'Нужно выбрать цвет' }),
      }),
    },
    onSubmit: ({ value }) => {
      onCreate?.({ color: value.color, name: value.name, description: '' })
    },
  })

  return (
    <form
      id="create-tag"
      className="w-full h-full"
      onSubmit={(e) => {
        e.preventDefault()
        e.stopPropagation()
        form.handleSubmit()
      }}
    >
      <Flex className="w-full" direction="column" gapY={20}>
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
                {field.state.meta.errors.map((err) => err?.message).join(',')}
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
        <Button
          form="create-tag"
          type="submit"
          mode="secondary"
          className="w-full mt-2"
        >
          Создать
        </Button>
      </Flex>
    </form>
  )
}
