import { $fetch } from 'ofetch'

/**
 * useApi — wraps $fetch with the Django token authentication header.
 * Usage: const { get, post, put, del } = useApi()
 */
export function useApi() {
  const { public: { apiBase } } = useRuntimeConfig()
  const authStore = useAuthStore()

  function headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' }
    if (authStore.token) {
      h['Authorization'] = `Token ${authStore.token}`
    }
    return h
  }

  async function get<T = unknown>(path: string, query?: Record<string, unknown>): Promise<T> {
    return $fetch<T>(`${apiBase}${path}`, {
      method: 'GET',
      headers: headers(),
      params: query,
    })
  }

  async function post<T = unknown>(path: string, body?: Record<string, unknown>): Promise<T> {
    return $fetch<T>(`${apiBase}${path}`, {
      method: 'POST',
      headers: headers(),
      body,
    })
  }

  async function put<T = unknown>(path: string, body?: Record<string, unknown>): Promise<T> {
    return $fetch<T>(`${apiBase}${path}`, {
      method: 'PUT',
      headers: headers(),
      body,
    })
  }

  async function del<T = unknown>(path: string): Promise<T> {
    return $fetch<T>(`${apiBase}${path}`, {
      method: 'DELETE',
      headers: headers(),
    })
  }

  return { get, post, put, del }
}
