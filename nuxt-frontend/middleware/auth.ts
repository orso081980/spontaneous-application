export default defineNuxtRouteMiddleware(() => {
  // Skip on the server — auth token lives in localStorage (client-only).
  // The client re-runs this middleware after hydration, so unauthenticated
  // users are still redirected; authenticated users are never bounced.
  if (import.meta.server) return
  const authStore = useAuthStore()
  if (!authStore.isAuthenticated) {
    return navigateTo('/login')
  }
})
