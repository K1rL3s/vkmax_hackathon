import type { TagResponse } from '@/lib/api/gen.schemas'
import {
  CellHeader,
  CellList,
  CellSimple,
  Container,
  Flex,
  Typography,
} from '@maxhub/max-ui'
import { clsx } from 'clsx'
import { Plus, X } from 'lucide-react'
import { DropDown } from '../ui/dropdown'
import { Card } from '../card'

export function TagsInput({
  value,
  onChange,
  options,
  disabled,
}: {
  value?: TagResponse[] | undefined
  onChange?: (tag: TagResponse) => void | undefined
  options?: TagResponse[] | undefined
  disabled?: boolean
}) {
  const tagColorStyles = {
    red: 'bg-red-700',
    blue: 'bg-blue-700',
    green: 'bg-green-700',
  }

  return (
    <Container className="w-full">
      <Flex direction="column" gapY={12}>
        <Typography.Headline variant="small" className="text-gray-400!">
          Теги
        </Typography.Headline>
        <Card>
          <CellSimple className="overflow-visible!" height="compact">
            <Flex direction="column" className="pb-2">
              <Flex wrap="wrap" className="py-1">
                {disabled && value?.length === 0 && (
                  <div className="mr-2 my-1 text-gray-500">
                    <Typography.Body>Нет тегов</Typography.Body>
                  </div>
                )}
                {value?.map((tag) => (
                  <div
                    onClick={() => !disabled && onChange?.(tag)}
                    className={clsx(
                      'rounded-full flex items-center space-x-2 px-2 py-1 w-fit mr-2 my-1',
                      tagColorStyles[tag.color as keyof typeof tagColorStyles],
                      { 'cursor-pointer': !disabled },
                    )}
                    key={tag.id}
                  >
                    <Typography.Title variant="small">
                      {tag.name}
                    </Typography.Title>
                    {!disabled && <X size={16} />}
                  </div>
                ))}
              </Flex>
              {!disabled && (
                <DropDown className="w-60">
                  <DropDown.Trigger>
                    <button
                      type="button"
                      className="rounded-full p-1 bg-(--accent-themed) mr-2 my-1 cursor-pointer hover:bg-(--states-background-hovered-themed) active:bg-(--states-background-hovered-themed)"
                    >
                      <Plus />
                    </button>
                  </DropDown.Trigger>
                  <DropDown.Content className="w-full mt-4.5 -ml-3">
                    <CellList
                      mode="full-width"
                      header={<CellHeader>Добавить тег</CellHeader>}
                    >
                      <>
                        <CellSimple
                          className="overflow-visible!"
                          height="compact"
                        >
                          <Flex wrap="wrap" className="py-1">
                            {disabled && value?.length === 0 && (
                              <div className="mr-2 my-1 text-gray-500">
                                <Typography.Body>Нет тегов</Typography.Body>
                              </div>
                            )}
                            {options
                              ?.filter((option) => !value?.includes(option))
                              .map((tag) => (
                                <DropDown.Item key={tag.id}>
                                  <div
                                    onClick={() => onChange?.(tag)}
                                    className={clsx(
                                      'rounded-full px-2 py-1 w-fit mr-2 my-1 cursor-pointer',
                                      tagColorStyles[
                                        tag.color as keyof typeof tagColorStyles
                                      ],
                                    )}
                                    key={tag.id}
                                  >
                                    <Typography.Title variant="small">
                                      {tag.name}
                                    </Typography.Title>
                                  </div>
                                </DropDown.Item>
                              ))}
                          </Flex>
                        </CellSimple>
                      </>
                    </CellList>
                  </DropDown.Content>
                </DropDown>
              )}
            </Flex>
          </CellSimple>
        </Card>
      </Flex>
    </Container>
  )
}
