import { useEffect } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useStartParams } from '@/integrations/max-ui/hooks/max-user'

export function ParamNavigatorLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const encryptedParams = useStartParams()
  const navigate = useNavigate()

  useEffect(() => {
    if (!encryptedParams) return

    try {
      const params = JSON.parse(atob(encryptedParams))
      if (params?.path) {
        navigate({ to: params.path })
      }
    } catch (e) {
      console.error('Invalid start params', e)
    }
  }, [encryptedParams, navigate])

  return children
}
