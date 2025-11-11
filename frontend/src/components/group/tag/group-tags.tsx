import { Flex, IconButton } from '@maxhub/max-ui'
import { Plus } from 'lucide-react'
import { useNavigate } from '@tanstack/react-router'
import { Tag } from '../../tag'
import type { TagResponse } from '@/lib/api/gen.schemas'
import { useDeleteTags } from '@/hooks/tags'

type GroupTagsInputPrpops = {
  tags?: Array<TagResponse>
  groupId?: number
}

export function GroupTags({ tags, groupId }: GroupTagsInputPrpops) {
  const navigate = useNavigate()
  const { mutate } = useDeleteTags()
  return (
    <>
      <div className="min-h-[52px] w-full rounded-(--size-border-radius-semantic-border-radius-card) cursor-pointer text-start px-3 py-2 bg-(--background-accent-neutral-fade-secondary) text-(--text-secondary)">
        <Flex wrap="wrap">
          {tags?.map((tag) => (
            <Tag
              onClick={() => mutate({ groupId: groupId!, tagId: tag.id })}
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
    </>
  )
}
