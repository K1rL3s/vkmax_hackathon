import { Outlet, createRootRouteWithContext } from '@tanstack/react-router'

import type { QueryClient } from '@tanstack/react-query'
import { RootLayout } from '@/components/layout/root-layout'
import { MaxBridgeLayout } from '@/components/layout/max-bridge-layout'
import { ParamNavigatorLayout } from '@/components/layout/param-navigator-layout'

interface RouterContext {
  queryClient: QueryClient
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: () => (
    <RootLayout>
      <MaxBridgeLayout>
        <ParamNavigatorLayout>
          <Outlet />
        </ParamNavigatorLayout>
      </MaxBridgeLayout>
    </RootLayout>
  ),
})
