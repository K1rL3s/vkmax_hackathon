import {
  Button,
  CellHeader,
  CellList,
  Container,
  Flex,
  Panel,
} from '@maxhub/max-ui'
import { createFileRoute } from '@tanstack/react-router'
import { useForm } from '@tanstack/react-form'
import type { NotifyMode } from '@/lib/api/gen.schemas'
import { Header } from '@/components/header'
import { RatioInput } from '@/components/ui/ratio-input'
import { TimezoneInput } from '@/components/timezone-input'
import { TIMEZONES } from '@/constants'
import { GroupTags } from '@/components/group/tag/group-tags'
import { usePersonalGroup } from '@/hooks/groups'
import { FallbackLoader } from '@/components/ui/fallback-loader'
import { useEditMe } from '@/hooks/user'

export const Route = createFileRoute('/settings')({
  component: SettingsPage,
})

function SettingsPage() {
  const { data, isPending } = usePersonalGroup()
  const { mutate } = useEditMe()

  const form = useForm({
    defaultValues: {
      notifyMode: data?.notifyMode ?? 'DEFAULT',
      timezone: TIMEZONES.find((tz) => tz.value === data?.timezone),
    },
    onSubmit: ({ value }) => {
      mutate({ notifyMode: value.notifyMode, timezone: value.timezone?.value })
      form.update({ defaultValues: value })
    },
  })

  return (
    <Flex className="h-screen w-full" direction="column" gapY={24}>
      <Header />
      <FallbackLoader isLoading={isPending}>
        <Panel className="w-full h-full pb-4">
          <Container className="w-full h-full">
            <form
              onSubmit={(e) => {
                e.preventDefault()
                e.stopPropagation()
                form.handleSubmit()
              }}
              className="w-full h-full"
            >
              <Flex
                className="h-full"
                direction="column"
                justify="space-between"
              >
                <Flex direction="column" gapY={24} className="w-full h-full">
                  <CellList
                    mode="island"
                    header={<CellHeader>Уведомления</CellHeader>}
                  >
                    <form.Field
                      name="notifyMode"
                      children={(field) => (
                        <RatioInput
                          value={
                            { DEFAULT: 0, SILENT: 1, DISABLE: 2 }[
                              field.state.value
                            ]
                          }
                          onChange={(option) => {
                            field.handleChange(
                              { 0: 'DEFAULT', 1: 'SILENT', 2: 'DISABLE' }[
                                option.id
                              ] as NotifyMode,
                            )
                          }}
                          options={[
                            { id: 0, label: 'По умолчанию' },
                            { id: 1, label: 'Тихо' },
                            { id: 2, label: 'Отключено' },
                          ]}
                        />
                      )}
                    />
                  </CellList>

                  <CellList
                    mode="island"
                    header={<CellHeader>Часовая зона</CellHeader>}
                  >
                    <form.Field
                      name="timezone"
                      children={(field) => (
                        <TimezoneInput
                          value={field.state.value}
                          onChange={(tz) => field.handleChange(() => tz as any)}
                        />
                      )}
                    />
                  </CellList>
                  <CellList
                    header={<CellHeader>Теги</CellHeader>}
                    mode="island"
                  >
                    <GroupTags
                      groupId={Number(data?.group.id)}
                      mode="primary"
                    />
                  </CellList>
                </Flex>
                <form.Subscribe
                  selector={(state) => state.isDefaultValue}
                  children={(state) =>
                    !state && (
                      <Button size="large" className="w-full" type="submit">
                        Изменить
                      </Button>
                    )
                  }
                />
              </Flex>
            </form>
          </Container>
        </Panel>
      </FallbackLoader>
    </Flex>
  )
}
