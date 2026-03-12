/**
 * useApplicationFilters — client-side filter state for the /applications page.
 *
 * Usage:
 *   const { search, status, filtered, clear } = useApplicationFilters(applicationsRef)
 */
export function useApplicationFilters(applications: Ref<JobApplication[] | null | undefined>) {
  const search = ref('')
  const country = ref('')
  const status = ref('')

  /** Unique non-empty countries derived from the loaded applications. */
  const countries = computed<CountryItem[]>(() => {
    const set = new Set<string>()
    for (const app of applications.value ?? []) {
      if (app.company_country) set.add(app.company_country)
    }
    return [...set].sort().map((name) => ({ name, flag: '🌍' }))
  })

  const filtered = computed<JobApplication[]>(() => {
    const list = applications.value ?? []
    const q = search.value.toLowerCase()
    return list.filter((app) => {
      if (q && !app.company_name.toLowerCase().includes(q)) return false
      if (country.value && app.company_country !== country.value) return false
      if (status.value && app.status !== status.value) return false
      return true
    })
  })

  function clear() {
    search.value = ''
    country.value = ''
    status.value = ''
  }

  return { search, country, countries, status, filtered, clear }
}
