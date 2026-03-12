import { $fetch, type FetchError } from 'ofetch'
import { ref } from 'vue'

/**
 * useAuth — composable for authentication actions against the Django API.
 *
 * Error handling maps HTTP status codes to user-friendly messages:
 *   400 / 422 → DRF field-validation errors joined into one string
 *   401       → "Invalid credentials. Please try again."
 *   409       → "Username already taken."
 *   500+      → "Server error. Please try again later."
 *   No response (network) → "Network error. Check your connection."
 */
export function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()
  const { public: { apiBase } } = useRuntimeConfig()

  const error = ref<string | null>(null)
  const loading = ref(false)

  async function login(username: string, password: string) {
    error.value = null
    loading.value = true
    try {
      const data = await $fetch<{ token: string; user_id: number; username: string; email: string; is_admin: boolean }>(
        `${apiBase}/auth/login/`,
        { method: 'POST', body: { username, password } }
      )
      authStore.setAuth(data.token, {
        id: data.user_id,
        username: data.username,
        email: data.email,
        is_staff: data.is_admin,
      })
      await router.push('/')
    } catch (e: unknown) {
      error.value = classifyError(e, 'login')
    } finally {
      loading.value = false
    }
  }

  async function register(username: string, email: string, password: string) {
    error.value = null
    loading.value = true
    try {
      const data = await $fetch<{ token: string; user_id: number; username: string; email: string; is_admin?: boolean }>(
        `${apiBase}/auth/register/`,
        { method: 'POST', body: { username, email, password } }
      )
      authStore.setAuth(data.token, {
        id: data.user_id,
        username: data.username,
        email: data.email,
        is_staff: data.is_admin ?? false,
      })
      await router.push('/')
    } catch (e: unknown) {
      error.value = classifyError(e, 'register')
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    const api = useApi()
    try {
      await api.post('/auth/logout/')
    } catch { /* ignore logout API errors */ } finally {
      authStore.logout()
      await router.push('/login')
    }
  }

  return { login, register, logout, error, loading }
}

// ── Error classification ──────────────────────────────────────────────────────

type AuthAction = 'login' | 'register'

function classifyError(e: unknown, action: AuthAction): string {
  // No response at all — network failure
  if (!e || typeof e !== 'object') return 'Network error. Check your connection.'

  const err = e as FetchError
  const status = err.status ?? err.response?.status

  // DRF validation errors (400 / 422): return the field messages joined
  if (status === 400 || status === 422) {
    const msg = extractFieldErrors(err.data ?? err.response?._data)
    if (msg) return msg
    return action === 'login'
      ? 'Invalid credentials. Please try again.'
      : 'Validation error. Please check your input.'
  }

  if (status === 401) return 'Invalid credentials. Please try again.'
  if (status === 409) return 'Username already taken.'

  if (status !== undefined && status >= 500) return 'Server error. Please try again later.'

  // No status (e.g. CORS / network timeout)
  return 'Network error. Check your connection.'
}

function extractFieldErrors(data: unknown): string | null {
  if (!data || typeof data !== 'object') return null
  const obj = data as Record<string, unknown>

  // DRF returns { detail: "…" } for non-field errors
  if (typeof obj.detail === 'string') return obj.detail

  // DRF returns { field: ["error1", "error2"], … } for field errors
  const messages = Object.values(obj)
    .flatMap((v) => (Array.isArray(v) ? v : [v]))
    .map((v) => String(v))
    .filter(Boolean)

  return messages.length > 0 ? messages.join(' ') : null
}

