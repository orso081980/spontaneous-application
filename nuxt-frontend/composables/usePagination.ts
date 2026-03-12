/**
 * usePagination — shared client-side pagination for any reactive array.
 *
 * Usage:
 *   const { page, totalPages, paginatedItems, visiblePages, goTo } = usePagination(itemsRef, 12)
 *
 * Automatically resets to page 1 whenever the source array changes (i.e. after a
 * filter is applied), so the user never lands on a now-empty page.
 */
export function usePagination<T>(items: Ref<T[] | null | undefined>, pageSize = 10) {
  const page = ref(1)

  const totalPages = computed(() => Math.ceil((items.value?.length ?? 0) / pageSize))

  const paginatedItems = computed<T[]>(() => {
    const start = (page.value - 1) * pageSize
    return (items.value ?? []).slice(start, start + pageSize)
  })

  /** Windowed page numbers — at most 5 visible, centred on the current page. */
  const visiblePages = computed<number[]>(() => {
    const total = totalPages.value
    const current = page.value
    const maxVisible = 5
    let start = Math.max(1, current - Math.floor(maxVisible / 2))
    let end = Math.min(total, start + maxVisible - 1)
    if (end - start + 1 < maxVisible) start = Math.max(1, end - maxVisible + 1)
    return Array.from({ length: end - start + 1 }, (_, i) => start + i)
  })

  function goTo(n: number) {
    page.value = Math.max(1, Math.min(n, totalPages.value || 1))
    if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Reset page when the source list changes (e.g. filters applied)
  watch(items, () => { page.value = 1 })

  return { page, totalPages, paginatedItems, visiblePages, goTo }
}
