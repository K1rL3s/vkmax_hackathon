import { useMaxUser } from '@/integrations/max-ui/hooks/max-user'
import axios from 'axios'
import type { AxiosError, AxiosRequestConfig } from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.API_URL || 'http://localhost:7001/',
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const { id } = useMaxUser()
  config.headers.set('master-id', id)
  return config
})

export const request = async <T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig,
): Promise<T> => {
  const source = axios.CancelToken.source()
  const promise = api({
    ...config,
    ...options,
    cancelToken: source.token,
  }).then((r) => r.data)

  // @ts-expect-error
  promise.cancel = () => {
    source.cancel()
  }

  return promise
}

export type BodyType<TData> = TData
export type ErrorType<TError> = AxiosError<TError>
