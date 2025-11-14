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

const TEST_WEB_APP_SESSION =
  'chat%3D%257B%2522id%2522%253A20103780%252C%2522type%2522%253A%2522DIALOG%2522%257D%26ip%3D176.222.223.156%26user%3D%257B%2522id%2522%253A85851413%252C%2522first_name%2522%253A%2522%25D0%2594%25D0%25B0%25D0%25BD%25D0%25B8%25D0%25B8%25D0%25BB%2522%252C%2522last_name%2522%253A%2522%2522%252C%2522username%2522%253Anull%252C%2522language_code%2522%253A%2522ru%2522%252C%2522photo_url%2522%253A%2522https%253A%252F%252Fi.oneme.ru%252Fi%253Fr%253DBTGBPUwtwgYUeoFhO7rESmr8_O-SzyDvfRoLuew3oXHc973nXxpx32aCKnFEhRnd5wk%2522%257D%26query_id%3D8d108b1e-56db-43ce-835e-e7a93fd8e2a3%26auth_date%3D1763042736%26hash%3D5020f1d18f0d75cbed48fb24b30a297d743f70ccd80ec6ba3807dea95369e589'

export function useMaxUser(): MaxUser {
  return {
    id: 7,
    maxId: 85851413,
    maxChatId: 20103780,
    maxPhoto: null,
    firstName: 'Даниил',
    lastName: 'Карпенко',
    phone: '890020045561',
    timezone: 300,
    notifyMode: 'DEFAULT',
  }
}

export function useInitData(): InitData {
  return window.WebApp.initDataUnsafe
}

export function useWebAppData(): string {
  return window.WebApp.initData ?? TEST_WEB_APP_SESSION
}

export function useStartParams() {
  return window.WebApp.initDataUnsafe.start_param
}

export function useCurrentUser(): UserData | undefined {
  return window.WebApp.initDataUnsafe.user
}
