import { useQuery } from '@tanstack/react-query'

const EVENTS_MOCK: Array<{
  id: number
  title: string
  date: Date
  tags: Array<{ id: number; name: string }>
  type: 'event' | 'message'
  group: {
    id: number
    name: string
  }
  creator: {
    firstName: string
    lastName: string
  }
}> = [
  {
    id: 35,
    title: 'Обсуждение проекта',
    date: new Date(2025, 5, 21),
    type: 'event',
    tags: [],
    group: {
      id: 1,
      name: 'Личное',
    },
    creator: { firstName: 'Екатерина', lastName: 'Смирнова' },
  },
  {
    id: 21,
    title: 'Обсуждение проекта',
    date: new Date(2025, 6, 9),
    type: 'event',
    tags: [],
    group: {
      id: 1,
      name: 'Личное',
    },
    creator: { firstName: 'Екатерина', lastName: 'Смирнова' },
  },
  {
    id: 18,
    title: 'Обсуждение проекта',
    date: new Date(2025, 8, 6),
    type: 'event',
    tags: [],
    group: {
      id: 2,
      name: 'Рабочее',
    },
    creator: { firstName: 'Екатерина', lastName: 'Смирнова' },
  },
  {
    id: 17,
    title: 'Обсуждение проекта',
    date: new Date(2025, 8, 9),
    type: 'event',
    tags: [],
    group: {
      id: 2,
      name: 'Рабочее',
    },
    creator: { firstName: 'Екатерина', lastName: 'Смирнова' },
  },
  {
    id: 1,
    title: 'Обсуждение проекта',
    date: new Date(2025, 8, 9),
    type: 'event',
    tags: [],
    group: {
      id: 2,
      name: 'Рабочее',
    },
    creator: { firstName: 'Екатерина', lastName: 'Смирнова' },
  },
  {
    id: 2,
    title: 'Обсуждение проекта',
    date: new Date(2025, 11, 9),
    type: 'event',
    tags: [],
    group: {
      id: 2,
      name: 'Рабочее',
    },
    creator: { firstName: 'Екатерина', lastName: 'Смирнова' },
  },
  {
    id: 3,
    title: 'Презентация нового продукта',
    date: new Date(2025, 11, 12),
    type: 'event',
    tags: [],
    group: {
      id: 2,
      name: 'Рабочее',
    },
    creator: { firstName: 'Алексей', lastName: 'Петров' },
  },
  {
    id: 4,
    title: 'Вебинар по новым технологиям',
    date: new Date(2026, 0, 1),
    type: 'message',
    group: {
      id: 1,
      name: 'Личное',
    },
    tags: [{ id: 1, name: 'технологии' }],
    creator: { firstName: 'Мария', lastName: 'Сидорова' },
  },
  {
    id: 5,
    title: 'Вебинар по этике',
    date: new Date(2026, 0, 1),
    type: 'message',
    group: {
      id: 1,
      name: 'Личное',
    },
    tags: [
      { id: 2, name: 'этика' },
      { id: 12, name: 'обучение' },
      { id: 27, name: 'комуникация' },
      { id: 28, name: 'презентация' },
      { id: 29, name: 'документация' },
    ],
    creator: { firstName: 'Мария', lastName: 'Сидорова' },
  },
  {
    id: 6,
    title: 'Вебинар по дизайну',
    date: new Date(2026, 1, 1),
    type: 'message',
    group: {
      id: 1,
      name: 'Личное',
    },
    tags: [{ id: 3, name: 'дизайн' }],
    creator: { firstName: 'Мария', lastName: 'Сидорова' },
  },
  {
    id: 7,
    title: 'Вебинар по управлению проектами',
    date: new Date(2026, 1, 1),
    type: 'message',
    group: {
      id: 1,
      name: 'Личное',
    },
    tags: [{ id: 4, name: 'управление проектами' }],
    creator: { firstName: 'Мария', lastName: 'Сидорова' },
  },
  {
    id: 8,
    title: 'Вебинар по тестированию',
    date: new Date(2026, 1, 1),
    type: 'message',
    group: {
      id: 1,
      name: 'Личное',
    },
    tags: [{ id: 5, name: 'тестирование' }],
    creator: { firstName: 'Мария', lastName: 'Сидорова' },
  },
  {
    id: 9,
    title: 'Вебинар по управлению проектами',
    date: new Date(2026, 2, 1),
    type: 'message',
    group: {
      id: 1,
      name: 'Личное',
    },
    tags: [{ id: 4, name: 'управление проектами' }],
    creator: { firstName: 'Мария', lastName: 'Сидорова' },
  },
  {
    id: 10,
    title: 'Вебинар по управлению проектами',
    date: new Date(2026, 2, 1),
    type: 'message',
    group: {
      id: 1,
      name: 'Личное',
    },
    tags: [{ id: 4, name: 'управление проектами' }],
    creator: { firstName: 'Мария', lastName: 'Сидорова' },
  },
  {
    id: 11,
    title: 'Вебинар по управлению проектами',
    date: new Date(2026, 2, 1),
    type: 'message',
    group: {
      id: 1,
      name: 'Личное',
    },
    tags: [{ id: 4, name: 'управление проектами' }],
    creator: { firstName: 'Мария', lastName: 'Сидорова' },
  },
  {
    id: 12,
    title: 'Вебинар по управлению проектами',
    date: new Date(2026, 2, 1),
    type: 'message',
    group: {
      id: 1,
      name: 'Личное',
    },
    tags: [{ id: 4, name: 'управление проектами' }],
    creator: { firstName: 'Мария', lastName: 'Сидорова' },
  },
]

export function useEventsList() {
  return useQuery({
    queryKey: ['events'],
    queryFn: (): Promise<
      Array<{
        id: number
        title: string
        date: Date
        type: 'event' | 'message'
        group: {
          id: number
          name: string
        }
        creator: { firstName: string; lastName: string }
      }>
    > => {
      return Promise.resolve(EVENTS_MOCK)
    },
  })
}

export function useEvent(id: number) {
  return useQuery({
    queryKey: ['events', id],
    queryFn: () =>
      Promise.resolve(EVENTS_MOCK.find((event) => event.id === id)),
  })
}
