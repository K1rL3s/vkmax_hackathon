import type { InitData, UserData } from '@/integrations/max-bridge'

export type MaxUser = {
  id: number
  maxId: number
  maxChatId: number
  maxPhoto: string | null
  firstName: string
  lastName: string
  phone: string
  timezone: number
  notifyMode: 'DEFAULT'
}

export function useInitData(): InitData {
  return window.WebApp.initDataUnsafe
}

export function useWebAppData(): string | null {
  return window.WebApp.initData
}

export function useStartParams() {
  return window.WebApp.initDataUnsafe.start_param
}

export function useCurrentUser(): UserData | undefined {
  return window.WebApp.initDataUnsafe.user
}
