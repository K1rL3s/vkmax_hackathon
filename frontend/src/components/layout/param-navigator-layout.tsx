import { Navigate } from '@tanstack/react-router'
import { useStartParams } from '@/integrations/max-ui/hooks/max-user'

export function ParamNavigatorLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const encryptedParams = useStartParams()
  if (!encryptedParams) {
    return children
  }
  const params = JSON.parse(atob(encryptedParams))
  if (params?.path) {
    return <Navigate to={params.path} />
  } else {
    return children
  }
}
