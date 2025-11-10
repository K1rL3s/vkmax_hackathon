import { Button, Typography } from '@maxhub/max-ui'
import { useState } from 'react'
import { useInvite } from '@/hooks/invite'

export function MemberInvite({ groupId }: { groupId: string }) {
  const { mutate, isPending } = useInvite()
  const [isCopied, setCopied] = useState(false)

  const handleInvite = () => {
    mutate(
      { groupId: Number(groupId) },
      {
        onSuccess: () => {
          setCopied(true)
          setTimeout(() => setCopied(false), 3000)
        },
      },
    )
  }

  return (
    <div className="pb-4 w-full">
      <Button
        size="large"
        className="w-full flex items-center"
        onClick={handleInvite}
        loading={isPending}
        disabled={isPending || isCopied}
      >
        <Typography.Headline variant="medium">
          {isCopied ? 'Скопировано' : 'Пригласить'}
        </Typography.Headline>
      </Button>
    </div>
  )
}
