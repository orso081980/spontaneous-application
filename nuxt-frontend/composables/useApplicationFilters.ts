/**
 * useApplicationFilters — client-side filter state for the /applications page.
 *
 * Usage:
 *   const { search, status, filtered, clear } = useApplicationFilters(applicationsRef)
 */
export function useApplicationFilters(applications: Ref<JobApplication[] | null | undefined>) {
  const search = ref('')
  const status = ref('')

  const filtered = computed<JobApplication[]>(() => {
    const list = applications.value ?? []
    const q = search.value.toLowerCase()
    return list.filter((app) => {
      if (q && !app.company_name.toLowerCase().includes(q)) return false
      if (status.value && app.status !== status.value) return false
      return true
    })
  })

  function clear() {
    search.value = ''
    status.value = ''
  }

  return { search, status, filtered, clear }
}
