import { Flex, Spinner } from '@maxhub/max-ui'

import { Header } from '../header'
import { useGroup } from '@/hooks/groups'

export function GroupPageLayout({
  groupId,
  children,
}: {
  groupId: number
  children: React.ReactNode
}) {
  const { data, isPending } = useGroup(groupId)

  return (
    <div className="w-full h-screen">
      <Flex className="h-full" direction="column" gapY={24}>
        {isPending ? (
          <div className="p-4">
            <Spinner />
          </div>
        ) : (
          <Flex direction="column" className="h-full w-full">
            <Header title={data?.group.name} />
            <div className="w-full h-full px-(--spacing-size-xl)">
              {children}
            </div>
          </Flex>
        )}
      </Flex>
    </div>
  )
}
