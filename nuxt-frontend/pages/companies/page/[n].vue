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
// Page number comes from the URL path segment (/companies/page/2 → page = 2)
const page = ref(Number(route.params.n) || 1);

// Redirect /companies/page/1 → /companies (canonical URL for page 1)
if (page.value <= 1) {
  await navigateTo(
    {
      path: "/companies",
      query: Object.fromEntries(Object.entries({ search: search.value, country: country.value, status: statusFilter.value }).filter(([, v]) => !!v)),
    },
    { replace: true },
  );
}

const countries = ref<CountryItem[]>([]);
const { data: countryData } = await useAsyncData("companies-page-n-countries", () => api.get<CountryItem[]>("/companies/countries/"));
countries.value = countryData.value ?? [];

const { data: userApps } = await useAsyncData(
  "companies-page-n-user-apps",
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

const {
  data: result,
  pending,
  refresh,
} = await useAsyncData(
  "companies-page-n-results",
  () =>
    api.get<CompaniesApiResponse>("/companies/paginated/", {
      page: page.value,
      page_size: pageSize,
      search: search.value || undefined,
      country: country.value || undefined,
      status: statusFilter.value || undefined,
    }),
  {
    server: !statusFilter.value,
    // Manual watch below — avoids the implicit Nuxt 4 client re-execute that causes
    // hydration mismatches when MongoDB returns results in a different order.
  },
);

// Keep page ref in sync with the URL param (browser back/forward, direct navigation).
watch(
  () => route.params.n,
  (n) => {
    page.value = Number(n) || 1;
  },
);

// Re-fetch on parameter changes (client-side only, after initial SSR payload is used).
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

watch(
  () => route.query,
  (q) => {
    search.value = (q.search as string) || "";
    country.value = (q.country as string) || "";
    statusFilter.value = (q.status as string) || "";
  },
);
</script>
