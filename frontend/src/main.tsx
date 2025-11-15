import ReactDOM from 'react-dom/client'
import { RouterProvider, createRouter } from '@tanstack/react-router'

import * as TanStackQueryProvider from './integrations/tanstack-query/root-provider.tsx'
import * as MaxUiProvider from './integrations/max-ui/root-provider.tsx'

import { routeTree } from './routeTree.gen'

import './styles.css'
import '@maxhub/max-ui/dist/styles.css'
import { NotFoundComponent } from './components/error/not-found.tsx'
import { ErrorComponent } from './components/error/error.tsx'

const TanStackQueryProviderContext = TanStackQueryProvider.getContext()
const router = createRouter({
  routeTree,
  context: {
    ...TanStackQueryProviderContext,
  },
  defaultPreload: 'intent',
  scrollRestoration: true,
  defaultStructuralSharing: true,
  defaultPreloadStaleTime: 0,

  defaultErrorComponent: () => <ErrorComponent />,
  defaultNotFoundComponent: () => <NotFoundComponent />,
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

const rootElement = document.getElementById('app')
if (rootElement && !rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement)
  root.render(
    <TanStackQueryProvider.Provider {...TanStackQueryProviderContext}>
      <MaxUiProvider.Provider>
        <RouterProvider router={router} />
      </MaxUiProvider.Provider>
    </TanStackQueryProvider.Provider>,
  )
}
