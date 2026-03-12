/**
 * useApplicationStatus — single source of truth for application status display.
 *
 * Replaces the duplicated statusLabel / statusClass helpers that previously lived
 * in both CompanyGrid.vue and applications/index.vue.
 */
export function useApplicationStatus() {
  const labels: Record<string, string> = {
    created: 'Created',
    sent: 'Sent',
    interview: 'Interview Stage',
    accepted: 'Accepted',
    refused: 'Refused',
  }

  function statusLabel(status: string): string {
    return labels[status] ?? status
  }

  /** Badge classes used in the applications list (slightly darker text). */
  function statusClass(status: string): string {
    const map: Record<string, string> = {
      created: 'bg-gray-100 text-gray-800',
      sent: 'bg-blue-100 text-blue-800',
      interview: 'bg-yellow-100 text-yellow-800',
      accepted: 'bg-green-100 text-green-800',
      refused: 'bg-red-100 text-red-800',
    }
    return map[status] ?? 'bg-gray-100 text-gray-600'
  }

  /** Badge classes used in CompanyGrid cards (slightly lighter text). */
  function statusBadgeClass(status: string): string {
    const map: Record<string, string> = {
      created: 'bg-gray-100 text-gray-700',
      sent: 'bg-blue-100 text-blue-700',
      interview: 'bg-yellow-100 text-yellow-700',
      accepted: 'bg-green-100 text-green-700',
      refused: 'bg-red-100 text-red-700',
    }
    return map[status] ?? 'bg-gray-100 text-gray-600'
  }

  /** Outlined button classes used on the company detail page. */
  function statusBtnClass(status: string): string {
    const map: Record<string, string> = {
      created: 'bg-gray-100 text-gray-700 border border-gray-300',
      sent: 'bg-blue-100 text-blue-700 border border-blue-200',
      interview: 'bg-yellow-100 text-yellow-700 border border-yellow-200',
      accepted: 'bg-green-100 text-green-700 border border-green-200',
      refused: 'bg-red-100 text-red-700 border border-red-200',
    }
    return map[status] ?? 'bg-gray-100 text-gray-600 border border-gray-200'
  }

  return { statusLabel, statusClass, statusBadgeClass, statusBtnClass }
}
