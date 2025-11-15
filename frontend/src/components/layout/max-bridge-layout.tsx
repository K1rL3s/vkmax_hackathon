import { Navigate } from '@tanstack/react-router'
import { FallbackLoader } from '../ui/fallback-loader'
import { useAuth } from '@/hooks/auth'

export function MaxBridgeLayout({ children }: { children: React.ReactNode }) {
  const { isPending, isError } = useAuth()

  if (isError) {
    return <Navigate to={'/max-error'} />
  }

  return <FallbackLoader isLoading={isPending}>{children}</FallbackLoader>
}
