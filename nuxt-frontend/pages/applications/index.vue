<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">My Applications</h1>
      <NuxtLink to="/companies" class="btn-primary"> <i class="fas fa-building mr-2"></i>Browse Companies </NuxtLink>
    </div>

    <!-- Loading skeleton -->
    <div v-if="pending" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="n in 6" :key="n" class="card animate-pulse">
        <div class="h-5 bg-gray-200 rounded w-2/3 mb-2"></div>
        <div class="h-4 bg-gray-100 rounded w-1/4 mb-4"></div>
        <div class="h-16 bg-gray-100 rounded"></div>
      </div>
    </div>

    <!-- No profile -->
    <div v-else-if="noProfile" class="text-center py-16 text-gray-500">
      <i class="fas fa-user-circle text-5xl mb-4 block text-gray-300"></i>
      <p class="mb-4"
        >You need to
        <NuxtLink to="/profile/edit" class="text-indigo-600 hover:underline">create your profile</NuxtLink>
        before you can apply to companies.
      </p>
    </div>

    <template v-else-if="applications?.length">
      <!-- Filter card -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Filter Applications</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <SearchInput v-model="filterSearch" label="Search by company" placeholder="Type company name…" />
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Filter by status</label>
            <select v-model="filterStatus" class="form-input">
              <option value="">All Statuses</option>
              <option value="created">Created</option>
              <option value="sent">Sent</option>
              <option value="interview">Interview Stage</option>
              <option value="accepted">Accepted</option>
              <option value="refused">Refused</option>
            </select>
          </div>
          <div class="flex items-end">
            <div class="w-full flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
              <p class="text-sm text-gray-600">
                Showing {{ filtered.length }} of {{ applications.length }} applications
                <span v-if="totalPages > 1"> (Page {{ page }} of {{ totalPages }})</span>
              </p>
              <button type="button" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium" @click="clearFilters"> Clear Filters </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 3-column grid -->
      <div v-if="paginatedItems.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="app in paginatedItems" :key="app.id" class="bg-white rounded-lg shadow-md p-5 flex flex-col">
          <!-- Header: company name + edit/delete -->
          <div class="flex justify-between items-start mb-3">
            <h3 class="text-base font-bold text-gray-900 flex-1 min-w-0 pr-2 leading-snug">
              {{ app.company_name }}
            </h3>
            <div class="flex gap-1.5 flex-shrink-0">
              <NuxtLink :to="`/applications/${app.id}/edit`" class="bg-blue-500 hover:bg-blue-600 text-white px-2.5 py-1 rounded text-xs font-medium"
                >Edit</NuxtLink
              >
              <button class="bg-red-500 hover:bg-red-600 text-white px-2.5 py-1 rounded text-xs font-medium" @click="deletingId = app.id">Delete</button>
            </div>
          </div>

          <!-- Status badge -->
          <div class="mb-3">
            <span class="px-3 py-1 rounded-full text-sm font-medium" :class="statusClass(app.status)">
              {{ statusLabel(app.status) }}
            </span>
          </div>

          <!-- Body -->
          <div class="space-y-3 text-sm flex-1">
            <div v-if="app.position">
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">Position</p>
              <p class="text-gray-800">{{ app.position }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">Applied</p>
              <p class="text-gray-800">{{ formatDate(app.created_at) }}</p>
            </div>

            <!-- Project suggestion -->
            <div v-if="hasContent(app.project_to_suggest)">
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">Project Suggestion</p>
              <div class="text-gray-700 prose prose-sm max-w-none" v-html="truncateHtml(app.project_to_suggest, 120)"></div>
            </div>

            <!-- Project link -->
            <div v-if="app.link_to_project">
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">Project Link</p>
              <a :href="app.link_to_project" target="_blank" class="text-indigo-600 hover:underline text-xs break-all">
                {{ shortenUrl(app.link_to_project) }}
              </a>
            </div>

            <!-- Message with expand/collapse -->
            <div v-if="hasContent(app.message)">
              <div class="flex items-center justify-between mb-0.5">
                <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide">Message</p>
                <button type="button" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium" @click="toggleExpanded(app.id)">
                  {{ isExpanded(app.id) ? "Show Less" : "Show More" }}
                </button>
              </div>
              <div class="text-gray-700 prose prose-sm max-w-none">
                <div v-if="isExpanded(app.id)" v-html="app.message"></div>
                <div v-else v-html="truncateHtml(app.message, 200)"></div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="flex gap-3 pt-3 border-t border-gray-100 mt-4">
            <NuxtLink :to="`/companies/${app.company_id}`" class="text-indigo-600 hover:text-indigo-800 font-medium text-sm"> View Company → </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <CompanyPagination v-if="totalPages > 1" :current-page="page" :total-pages="totalPages" @page="goTo" />

      <!-- No results after filtering -->
      <div v-else-if="!paginatedItems.length" class="text-center py-12 text-gray-400">
        <i class="fas fa-filter text-3xl mb-3 block"></i>
        No applications match the current filters.
      </div>
    </template>

    <!-- Empty state -->
    <div v-else class="text-center py-16 text-gray-400">
      <i class="fas fa-inbox text-5xl mb-4 block"></i>
      No applications yet.
      <NuxtLink to="/companies" class="text-indigo-600 hover:underline">Browse companies</NuxtLink>
    </div>

    <!-- Delete confirmation modal -->
    <div v-if="deletingId" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="card max-w-sm w-full mx-4">
        <h3 class="font-semibold text-lg mb-2">Delete application?</h3>
        <p class="text-gray-600 text-sm mb-5">This action cannot be undone.</p>
        <div class="flex gap-3 justify-end">
          <button class="btn-secondary" @click="deletingId = null">Cancel</button>
          <button class="btn-danger" @click="deleteApp">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const api = useApi();
const { statusLabel, statusClass } = useApplicationStatus();
const noProfile = ref(false);

const {
  data: applications,
  pending,
  refresh,
} = await useAsyncData(
  "applications",
  async () => {
    try {
      return await api.get<JobApplication[]>("/applications/");
    } catch (e: unknown) {
      const err = e as Record<string, unknown>;
      if (err?.status === 400 || (err?.data as Record<string, unknown>)?.detail) {
        noProfile.value = true;
      }
      return null;
    }
  },
  { server: false },
);

// ── Filters (composable) ──────────────────────────────────────────────────────
const { search: filterSearch, status: filterStatus, filtered, clear: clearFilters } = useApplicationFilters(applications);

// ── Pagination (composable) ───────────────────────────────────────────────────
const PAGE_SIZE = 9;
const { page, totalPages, paginatedItems, goTo } = usePagination(filtered, PAGE_SIZE);

// ── Expand / collapse message ─────────────────────────────────────────────────
const expandedIds = ref<string[]>([]);

function toggleExpanded(id: string) {
  const idx = expandedIds.value.indexOf(id);
  if (idx >= 0) expandedIds.value.splice(idx, 1);
  else expandedIds.value.push(id);
}

function isExpanded(id: string) {
  return expandedIds.value.includes(id);
}

// ── Delete ────────────────────────────────────────────────────────────────────
const deletingId = ref<string | null>(null);

async function deleteApp() {
  if (!deletingId.value) return;
  await api.del(`/applications/${deletingId.value}/`);
  deletingId.value = null;
  refresh();
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function hasContent(html: string | null | undefined): boolean {
  if (!html) return false;
  return html.replace(/<[^>]*>/g, "").trim().length > 0;
}

function truncateHtml(html: string, maxLen: number): string {
  const plain = html
    .replace(/<[^>]*>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (plain.length <= maxLen) return html;
  return `<p>${plain.slice(0, maxLen)}…</p>`;
}

function shortenUrl(url: string): string {
  try {
    return new URL(url).hostname;
  } catch {
    return url;
  }
}
</script>
