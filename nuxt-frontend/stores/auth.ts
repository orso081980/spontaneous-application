import { defineStore } from 'pinia'

interface User {
  id: number
  username: string
  email: string
  is_staff: boolean
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null as string | null,
    user: null as User | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => !!state.user?.is_staff,
  },

  actions: {
    // Called in app.vue to rehydrate state from localStorage
    init() {
      if (typeof window !== 'undefined') {
        const stored = localStorage.getItem('auth_token')
        const storedUser = localStorage.getItem('auth_user')
        if (stored) this.token = stored
        if (storedUser) {
          try { this.user = JSON.parse(storedUser) } catch { /* ignore */ }
        }
      }
    },

    setAuth(token: string, user: User) {
      this.token = token
      this.user = user
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', token)
        localStorage.setItem('auth_user', JSON.stringify(user))
      }
    },

    logout() {
      this.token = null
      this.user = null
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
      }
    },
  },
})
