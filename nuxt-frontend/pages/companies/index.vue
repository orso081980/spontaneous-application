<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Companies</h1>
      <div class="flex gap-2">
        <NuxtLink to="/companies/map" class="btn-secondary"> <i class="fas fa-map-marker-alt mr-2"></i>Map view </NuxtLink>
        <NuxtLink v-if="auth.isAdmin" to="/admin/companies/create" class="btn-primary"> <i class="fas fa-plus mr-2"></i>Add company </NuxtLink>
      </div>
    </div>

    <CompanyFilterCard
      v-model:search="search"
      v-model:country="country"
      v-model:statusFilter="statusFilter"
      :countries="countries"
      :total-showing="result?.pagination.total_items ?? 0"
      :current-page="page"
      :total-pages="result?.pagination.total_pages"
      :show-status-filter="isAuthenticated"
      @search="onFilterSearch"
      @clear="clearFilters"
    />

    <CompanyGrid :companies="result?.results ?? []" :pending="!!pending" :page-size="pageSize" :app-status-map="appStatusMap" />

    <CompanyPagination
      v-if="result && result.pagination.total_pages > 1"
      :current-page="page"
      :total-pages="result.pagination.total_pages"
      @page="onPageChange"
    />
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore();
const api = useApi();
const route = useRoute();
const router = useRouter();

const isAuthenticated = ref(false);
onMounted(() => {
  isAuthenticated.value = auth.isAuthenticated;
});

const pageSize = 12;

const search = ref((route.query.search as string) || "");
const country = ref((route.query.country as string) || "");
const statusFilter = ref((route.query.status as string) || "");
// Page 1 lives at /companies (index), page N at /companies/page/N
const page = ref(1);

// Redirect legacy ?page= query-param URLs to the new path-based scheme
if (route.query.page && Number(route.query.page) > 1) {
  const legacyPage = Number(route.query.page);
  const { page: _p, ...rest } = route.query as Record<string, string>;
  await navigateTo({ path: `/companies/page/${legacyPage}`, query: rest }, { replace: true });
}

const countries = ref<CountryItem[]>([]);
const { data: countryData } = await useAsyncData("countries", () => api.get<CountryItem[]>("/companies/countries/"));
countries.value = countryData.value ?? [];

// appStatusMap is used by CompanyGrid for status badges (loaded client-side)
const { data: userApps } = await useAsyncData(
  "companies-page-user-apps",
  async () => {
    if (!auth.isAuthenticated) return [] as JobApplication[];
    try {
      return await api.get<JobApplication[]>("/applications/");
    } catch {
      return [] as JobApplication[];
    }
  },
  { server: false, lazy: true },
);
const appStatusMap = computed(() => new Map((userApps.value ?? []).map((a) => [a.company_id, a.status])));

// Status filtering requires the auth token (server-side Django filtering).
// We skip SSR when a status filter is active so the token is always available.
const {
  data: result,
  pending,
  refresh,
} = await useAsyncData(
  "paginated-companies",
  () =>
    api.get<CompaniesApiResponse>("/companies/paginated/", {
      page: page.value,
      page_size: pageSize,
      search: search.value || undefined,
      country: country.value || undefined,
      status: statusFilter.value || undefined,
    }),
  {
    // Disable SSR when a status filter is active — the token lives in localStorage
    // and is unavailable on the server, so the backend would return "Not applied"
    // results instead of the correct filtered set.
    server: !statusFilter.value,
    // DO NOT use the watch option here — it causes Nuxt 4 to schedule an implicit
    // client-side re-execute on mount, which can return results in a different order
    // from MongoDB and produce a hydration mismatch.
  },
);

// Re-fetch when any filter parameter changes (client-side only, after initial SSR).
watch([page, search, country, statusFilter], () => refresh());

function buildPath(p: number) {
  return p <= 1 ? "/companies" : `/companies/page/${p}`;
}

function buildQuery() {
  const q: Record<string, string> = {};
  if (search.value) q.search = search.value;
  if (country.value) q.country = country.value;
  if (statusFilter.value) q.status = statusFilter.value;
  return q;
}

function onFilterSearch() {
  page.value = 1;
  router.push({ path: "/companies", query: buildQuery() });
}

function onPageChange(n: number) {
  page.value = n;
  router.push({ path: buildPath(n), query: buildQuery() });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function clearFilters() {
  search.value = "";
  country.value = "";
  statusFilter.value = "";
  page.value = 1;
  router.push("/companies");
}

// Sync refs when URL changes (back/forward navigation)
watch(
  () => route.query,
  (q) => {
    search.value = (q.search as string) || "";
    country.value = (q.country as string) || "";
    statusFilter.value = (q.status as string) || "";
  },
);
</script>
