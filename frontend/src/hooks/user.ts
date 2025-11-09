import { useQuery } from '@tanstack/react-query'

type User = {
  maxId: string
  username: string
  firstName: string
}

const USER_MOCK: User = {
  maxId: '1',
  username: 'john_doe',
  firstName: 'John',
}

export function useUser() {
  return useQuery({
    queryKey: ['user'],
    queryFn: () => {
      return Promise.resolve(USER_MOCK)
    },
  })
}
