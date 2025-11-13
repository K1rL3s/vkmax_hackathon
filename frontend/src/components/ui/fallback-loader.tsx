import { Spinner } from '@maxhub/max-ui'

export function FallbackLoader({
  isLoading,
  size,
  children,
}: {
  isLoading: boolean
  size?: number
  children: React.ReactNode
}) {
  if (isLoading) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <Spinner size={size ?? 32} />
      </div>
    )
  }

  return children
}
