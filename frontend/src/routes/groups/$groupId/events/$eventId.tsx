import {
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
import { Tag } from '@/components/tag'
import { useGroup } from '@/hooks/groups'

export const Route = createFileRoute('/groups/$groupId/events/$eventId')({
  component: EventDetailsPage,
})

function EventDetailsPage() {
  const { groupId, eventId } = useParams({
    from: '/groups/$groupId/events/$eventId',
  })

  useGroup(Number(groupId))
  const eventQuery = useEvent(Number(eventId))

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
      {eventQuery.isPending ? (
        <Loader size={38} />
      ) : (
        <CellList className="w-full" mode="island" filled>
          <CellSimple
            before={
              <Typography.Label className="w-16 text-start">
                Название
              </Typography.Label>
            }
            title={eventQuery.data?.title}
          />
          <CellSimple
            before={
              <Typography.Label className="w-16 text-start">
                Описание
              </Typography.Label>
            }
          >
            {eventQuery.data?.description}
          </CellSimple>
          <CellSimple
            before={
              <Typography.Label className="w-16 text-start">
                Теги
              </Typography.Label>
            }
          >
            <Flex wrap="wrap">
              {eventQuery.data?.tags.length === 0 && (
                <Typography.Body className="text-sm">
                  Теги не установлены
                </Typography.Body>
              )}
              {eventQuery.data?.tags.map((tag) => (
                <Tag tag={tag} />
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
              {eventQuery.data?.group.name}
            </span>
          </CellSimple>
        </CellList>
      )}
    </DynamicPageLayout>
  )
}
