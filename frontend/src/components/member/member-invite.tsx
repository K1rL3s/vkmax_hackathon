import { Button, Typography } from '@maxhub/max-ui'
import { useInvite } from '@/hooks/invite'
import { useState } from 'react'

export function MemberInvite({ groupId }: { groupId: number }) {
  const { mutate, isPending } = useInvite()
  const [isCopied, setCopied] = useState(false)

  const handleInvite = () => {
    setCopied(true)
    setTimeout(() => setCopied(false), 1000)
    mutate(
      { groupId },
      {
        onSuccess: () => {},
      },
    )
  }

  return (
    <div className="pb-4 w-full">
      <Button
        size="large"
        className="w-full flex items-center"
        onClick={handleInvite}
        disabled={isPending || isCopied}
      >
        <Typography.Headline variant="medium">
          {isCopied ? 'Скопировано' : 'Пригласить'}
        </Typography.Headline>
      </Button>
    </div>
  )
}
