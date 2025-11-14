import { Flex, IconButton } from '@maxhub/max-ui'
import { Plus } from 'lucide-react'
import { useNavigate } from '@tanstack/react-router'
import { clsx } from 'clsx'
import { Tag } from '../../tag'
import type { TagResponse } from '@/lib/api/gen.schemas'
import { useDeleteTags, useGroupTags } from '@/hooks/tags'
import { FallbackLoader } from '@/components/ui/fallback-loader'

type GroupTagsInputPrpops = {
  tags?: Array<TagResponse>
  groupId: number
  mode?: 'primary' | 'secondary'
}

export function GroupTags({
  groupId,
  mode = 'secondary',
}: GroupTagsInputPrpops) {
  const navigate = useNavigate()
  const { data, isPending } = useGroupTags(groupId)
  const { mutate } = useDeleteTags()
  return (
    <FallbackLoader isLoading={isPending}>
      <div
        className={clsx(
          'min-h-[52px] w-full rounded-(--size-border-radius-semantic-border-radius-card) cursor-pointer text-start px-3 py-2',
          {
            'bg-(--background-accent-neutral-fade-secondary) text-(--text-secondary)':
              mode === 'secondary',
          },
          {
            'bg-(--background-surface-card) text-(--text-primary)':
              mode === 'primary',
          },
        )}
      >
        <Flex wrap="wrap">
          {data?.map((tag) => (
            <Tag
              onClick={() => mutate({ groupId: groupId, tagId: tag.id })}
              key={tag.id}
              tag={tag}
            />
          ))}
          <IconButton
            type="button"
            onClick={() =>
              navigate({
                to: '/groups/$groupId/tags/create',
                params: { groupId: String(groupId) },
              })
            }
            className="rounded-full!"
          >
            <Plus />
          </IconButton>
        </Flex>
      </div>
    </FallbackLoader>
  )
}
