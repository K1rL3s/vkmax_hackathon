import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { UserUpdateRequest } from '@/lib/api/gen.schemas'
import {
  getUserByIdRouteUsersMeGet,
  updateUserRouteUsersPatch,
} from '@/lib/api/users/users'

export function useMe() {
  return useQuery({
    queryKey: ['me'],
    queryFn: () => getUserByIdRouteUsersMeGet(),
  })
}

export function useEditMe() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationKey: ['me', 'edit'],
    mutationFn: (input: UserUpdateRequest) => updateUserRouteUsersPatch(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['me'] })
    },
  })
}
