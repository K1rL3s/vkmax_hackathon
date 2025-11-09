import { Calendar, Plus, User } from 'lucide-react'

export const routes: Record<
  string,
  { title: string; icon: React.ElementType; sidebar: boolean }
> = {
  '/': {
    title: 'Расписание',
    icon: Calendar,
    sidebar: true,
  },
  '/profile': {
    title: 'Профиль',
    icon: User,
    sidebar: true,
  },
  '/groups/create': {
    title: 'Создать группу',
    icon: Plus,
    sidebar: false,
  },
}
