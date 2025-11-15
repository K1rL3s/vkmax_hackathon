import { useNavigate } from '@tanstack/react-router'
import { useStartParams } from '@/integrations/max-ui/hooks/max-user'

export function ParamNavigatorLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const navigate = useNavigate()
  const encryptedParams = useStartParams()
  if (!encryptedParams) {
    return children
  }

  const params = JSON.parse(atob(encryptedParams))
  if (params?.path) {
    navigate(params.path)
  } else {
    return children
  }
}
