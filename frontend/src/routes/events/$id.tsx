import {
  Avatar,
  CellList,
  CellSimple,
  Flex,
  Grid,
  ToolButton,
  Typography,
} from '@maxhub/max-ui'
import { createFileRoute, useParams } from '@tanstack/react-router'
import { Edit2, Trash2Icon } from 'lucide-react'
import { DynamicPageLayout } from '@/components/layout/dynamic-page-layout'
import { Loader } from '@/components/ui/loader'
import { useEvent } from '@/hooks/events'

export const Route = createFileRoute('/events/$id')({
  component: EventDetailsPage,
})

function EventDetailsPage() {
  const { id } = useParams({ from: '/events/$id' })
  const { data, isPending } = useEvent(Number(id))

  return (
    <DynamicPageLayout
      footer={
        <Flex
          className="w-full py-1 px-3 bg-(--background-surface-card) rounded-t-4xl"
          gapX={12}
          justify="center"
        >
          <Grid cols={2} gapX={8}>
            <ToolButton
              onClick={() => console.log(1)}
              icon={<Edit2 size={24} />}
            >
              Изменить
            </ToolButton>
            <ToolButton icon={<Trash2Icon size={24} />}>Удалить</ToolButton>
          </Grid>
        </Flex>
      }
    >
      {isPending ? (
        <Loader size={38} />
      ) : (
        <CellList className="w-full" mode="island" filled>
          <CellSimple
            before={
              <Typography.Label className="w-16 text-start">
                Название
              </Typography.Label>
            }
            title={data?.title}
          />
          <CellSimple
            before={
              <Typography.Label className="w-16 text-start">
                Дата
              </Typography.Label>
            }
            title={data?.date.toLocaleDateString('ru', {
              weekday: 'short',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          />
          <CellSimple
            before={
              <Typography.Label className="w-16 text-start">
                Теги
              </Typography.Label>
            }
          >
            <Flex wrap="wrap">
              {data?.tags.length === 0 && (
                <Typography.Body className="text-sm">
                  Теги не установлены
                </Typography.Body>
              )}
              {data?.tags.map((tag) => (
                <span
                  className="rounded-full mr-1 mb-2 px-2 pb-1 bg-(--accent-themed)"
                  key={tag.id}
                >
                  {tag.name}
                </span>
              ))}
            </Flex>
          </CellSimple>
          <CellSimple
            before={
              <Typography.Label className="w-16 text-start">
                Группа
              </Typography.Label>
            }
          >
            <span className="px-2 pb-1 bg-(--accent-themed) rounded-full w-fit">
              {data?.group.name}
            </span>
          </CellSimple>
          <CellSimple
            before={
              <Typography.Label className="w-16 text-start">
                Создатель
              </Typography.Label>
            }
          >
            <Flex align="center" gapX={12}>
              <Avatar.Container>
                <Avatar.Text>
                  {data?.creator.firstName.charAt(0).toUpperCase()}
                  {data?.creator.lastName.charAt(0).toUpperCase()}
                </Avatar.Text>
              </Avatar.Container>
              {`${data?.creator.firstName} ${data?.creator.lastName.charAt(0).toUpperCase()}.`}
            </Flex>
          </CellSimple>
        </CellList>
      )}
    </DynamicPageLayout>
  )
}
