import {
  Button,
  CellHeader,
  CellInput,
  CellList,
  Container,
  Flex,
  Panel,
  Typography,
} from '@maxhub/max-ui'
import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import {  useForm } from '@tanstack/react-form'
import { z } from 'zod'
import { clsx } from 'clsx'
import { LucideMessageCircleWarning } from 'lucide-react'
import type {StandardSchemaV1Issue} from '@tanstack/react-form';
import { Header } from '@/components/header'
import { Avatar } from '@/components/avatar'
import { useEditMe, useMe } from '@/hooks/user'
import { TimezoneInput } from '@/components/timezone-input'
import { TIMEZONES } from '@/components/timezone-select-modal'
import { FallbackLoader } from '@/components/ui/fallback-loader'

export const Route = createFileRoute('/profile')({
  component: ProfilePage,
})

function ProfilePage() {
  const { data, isPending } = useMe()
  const [isEditing, setIsEditing] = useState(false)
  const editMeMutation = useEditMe()

  const form = useForm({
    defaultValues: {
      firstName: data?.firstName ?? '',
      lastName: data?.lastName ?? '',
      phone: data?.phone ?? '',
      timezone:
        TIMEZONES.find((tz) => tz.value === data?.timezone) ?? TIMEZONES[0],
    },
    validators: {
      onChange: z.object({
        firstName: z.string().min(1, { error: 'Имя не может быть пустым' }),
        lastName: z.string().min(1, { error: 'Фамилия не может быть пустой' }),
        phone: z.string().min(1, { error: 'Телефон не может быть пустым' }),
        timezone: z.object({
          label: z.string(),
          value: z.number(),
        }),
      }),
    },
    onSubmit: ({ value }) => {
      editMeMutation.mutate(value, { onSuccess: () => setIsEditing(false) })
    },
  })

  return (
    <Flex className="h-screen" direction="column" gapY={24}>
      <Header />
      <Panel className="w-full h-full pb-4">
        <FallbackLoader isLoading={false}>
          <form
            onSubmit={(e) => {
              e.preventDefault()
              e.stopPropagation()
              form.handleSubmit()
            }}
            className="w-full h-full"
          >
            <Container className="h-full w-full">
              <Flex
                className="w-full h-full"
                justify="space-between"
                direction="column"
              >
                <Flex className="w-full h-full" direction="column" gapY={34}>
                  <Flex className="w-full" justify="center">
                    <Avatar
                      size={88}
                      firstName={data?.firstName ?? ''}
                      lastName={data?.lastName ?? ''}
                    />
                    <Typography.Headline>
                      {data?.firstName} {data?.lastName}
                    </Typography.Headline>
                  </Flex>
                  <Flex direction="column" className="w-full">
                    <CellList
                      filled
                      mode="island"
                      header={
                        <CellHeader className="mb-2">Личные данные</CellHeader>
                      }
                    >
                      <form.Field
                        name="firstName"
                        children={(field) => (
                          <CellInput
                            disabled={!isEditing}
                            before={'Имя'}
                            innerClassNames={{
                              before: {
                                'text-red-500': field.state.meta.errors.length,
                              },
                            }}
                            value={field.state.value}
                            onChange={(e) => field.handleChange(e.target.value)}
                          />
                        )}
                      />
                      <form.Field
                        name="lastName"
                        children={(field) => (
                          <CellInput
                            innerClassNames={{
                              before: {
                                'text-red-500': field.state.meta.errors.length,
                              },
                            }}
                            disabled={!isEditing}
                            before={'Фамилия'}
                            value={field.state.value}
                            onChange={(e) => field.handleChange(e.target.value)}
                          />
                        )}
                      />
                      <form.Field
                        name="phone"
                        children={(field) => (
                          <CellInput
                            innerClassNames={{
                              before: {
                                'text-red-500': field.state.meta.errors.length,
                              },
                              body: clsx('text-(--accent-themed)', {
                                'text-(--states-text-disabled-primary)!':
                                  !isEditing,
                              }),
                            }}
                            disabled={!isEditing}
                            before={'Телефон'}
                            value={field.state.value}
                            onChange={(e) => field.handleChange(e.target.value)}
                          />
                        )}
                      />
                    </CellList>
                  </Flex>
                  <CellList
                    filled
                    mode="island"
                    header={<CellHeader className="mb-2">Настройки</CellHeader>}
                  >
                    <form.Field
                      name="timezone"
                      children={(field) => (
                        <TimezoneInput
                          disabled={!isEditing}
                          value={field.state.value}
                          before={
                            <Typography.Title
                              className={clsx('text-(--text-primary)', {
                                'text-(--states-text-disabled-primary)!':
                                  !isEditing,
                              })}
                            >
                              Часовой пояс
                            </Typography.Title>
                          }
                          mode="primary"
                          onChange={field.handleChange}
                        />
                      )}
                    />
                  </CellList>
                </Flex>
                <Flex className="w-full" gapX={10}>
                  {!isEditing ? (
                    <>
                      <Button
                        type="button"
                        key={'edit'}
                        onClick={() => setIsEditing(true)}
                        appearance="neutral-themed"
                        mode="secondary"
                        className="w-full"
                      >
                        Изменить
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button
                        key={'submit'}
                        type="submit"
                        appearance="themed"
                        mode="primary"
                        className="w-full flex-2"
                      >
                        Подтвердить
                      </Button>
                      <Button
                        type="button"
                        key={'cancel'}
                        appearance="negative"
                        mode="secondary"
                        className="flex-1"
                        onClick={() => {
                          form.reset()
                          setIsEditing(false)
                        }}
                      >
                        Отменить
                      </Button>
                    </>
                  )}
                </Flex>
              </Flex>
            </Container>
          </form>
        </FallbackLoader>
      </Panel>
    </Flex>
  )
}
