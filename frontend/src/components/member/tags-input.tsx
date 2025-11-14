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
import type { TagResponse } from '@/lib/api/gen.schemas'

export function TagsInput({
  value,
  onChange,
  options,
  disabled,
  header,
  before,
  fullWidth,
  className,
}: {
  value?: Array<TagResponse> | undefined
  onChange?: (tag: TagResponse) => void | undefined
  options?: Array<TagResponse> | undefined
  disabled?: boolean
  header?: React.ReactNode
  before?: React.ReactNode
  fullWidth?: boolean
  className?: string
}) {
  const tagColorStyles = {
    red: 'bg-red-500',
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    purple: 'bg-purple-500',
    cyan: 'bg-cyan-500',
    pink: 'bg-pink-500',
    orange: 'bg-orange-500',
  }

  return (
    <Container className={clsx('w-full', className)}>
      <Flex direction="column" gapY={12}>
        {header}
        <Card>
          <CellSimple
            className={clsx('overflow-visible!', { 'px-0!': fullWidth })}
            height="compact"
          >
            <Flex align="center" gapX={10}>
              {before}
              <Flex direction="column" className="pb-2">
                <Flex wrap="wrap" className="py-1">
                  {disabled ||
                    (value?.length === 0 && (
                      <div className="mr-2 my-1 text-gray-500">
                        <Typography.Body>Нет тегов</Typography.Body>
                      </div>
                    ))}
                  {value?.map((tag) => (
                    <div
                      onClick={() => !disabled && onChange?.(tag)}
                      className={clsx(
                        'rounded-full flex items-center space-x-2 px-2 py-1 w-fit mr-2 my-1',
                        tagColorStyles[
                          tag.color as keyof typeof tagColorStyles
                        ],
                        { 'cursor-pointer': !disabled },
                      )}
                      key={tag.id}
                    >
                      <Typography.Title
                        className="text-(--text-contrast-static)"
                        variant="small"
                      >
                        {tag.name}
                      </Typography.Title>
                      {!disabled && (
                        <X
                          color="currentColor"
                          className="text-(--text-contrast-static)"
                          size={16}
                        />
                      )}
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
                        <Plus
                          color="currentColor"
                          className="text-(--text-contrast-static)"
                        />
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
                              {options?.length === 0 && (
                                <div className="mr-2 my-1 text-gray-500">
                                  <Typography.Body>Нет тегов</Typography.Body>
                                </div>
                              )}
                              {options
                                ?.filter(
                                  (option) =>
                                    !value
                                      ?.map((v) => v.id)
                                      .includes(option.id),
                                )
                                .map((tag) => (
                                  <DropDown.Item key={tag.id}>
                                    <div
                                      onClick={() => onChange?.(tag)}
                                      className={clsx(
                                        'rounded-full px-2 py-1 w-fit mr-2 my-1 cursor-pointer text-(--text-contrast-static)',
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
            </Flex>
          </CellSimple>
        </Card>
      </Flex>
    </Container>
  )
}
