<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Company Board</h1>
        <p class="mt-1 text-gray-500">Browse companies and track your spontaneous applications</p>
      </div>
      <NuxtLink to="/companies" class="btn-primary"> <i class="fas fa-building mr-2"></i>All Companies </NuxtLink>
    </div>

    <!-- Filter + grid are 100% client-side (server:false fetch).
         <ClientOnly> prevents Vue from hydrating these nodes — the SSR HTML
         shows the skeleton fallback, and after JS loads the real content mounts.
         Without this, server renders empty-state (pending=false, data=null) while
         the client hydrates with pending=true → structure mismatch. -->
    <ClientOnly>
      <CompanyFilterCard
        v-model:search="filterSearch"
        v-model:country="filterCountry"
        v-model:statusFilter="filterStatus"
        :countries="countries"
        :total-showing="filtered.length"
        :show-status-filter="auth.isAuthenticated"
        @clear="clearFilters"
      />
      <CompanyGrid :companies="filtered" :pending="!!pending" :app-status-map="appStatusMap" />
      <template #fallback>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="n in 9" :key="n" class="card animate-pulse">
            <div class="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
            <div class="h-4 bg-gray-100 rounded w-1/2"></div>
          </div>
        </div>
      </template>
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
const api = useApi();
const auth = useAuthStore();

// No isAuthenticated ref needed — filter card is inside <ClientOnly>, so it only
// ever runs on the client where auth.isAuthenticated is already accurate.

const filterSearch = ref("");
const filterCountry = ref("");
const filterStatus = ref("");

const { data: companies, pending } = await useAsyncData(
  "home-companies",
  () => api.get<Company[]>("/companies/"),
  // server: false — all filtering is client-side and MongoDB's natural ordering can
  // differ between the SSR request and the client payload, causing hydration mismatches.
  // A loading skeleton is shown until JS loads (handled by CompanyGrid's pending state).
  { server: false },
);

const { data: countriesData } = await useAsyncData("home-countries", () => api.get<CountryItem[]>("/companies/countries/"));
const countries = computed(() => countriesData.value ?? []);

// Load user applications client-side for status badges + filter
const { data: userApps } = await useAsyncData(
  "home-user-apps",
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

const filtered = computed(() => {
  const list = companies.value ?? [];
  return list.filter((c) => {
    if (filterSearch.value) {
      if (!c.name.toLowerCase().includes(filterSearch.value.toLowerCase())) return false;
    }
    if (filterCountry.value && !c.address?.includes(filterCountry.value)) return false;
    if (filterStatus.value) {
      const appStatus = appStatusMap.value.get(c.id);
      if (filterStatus.value === "not-applied") return !appStatus;
      return appStatus === filterStatus.value;
    }
    return true;
  });
});

function clearFilters() {
  filterSearch.value = "";
  filterCountry.value = "";
  filterStatus.value = "";
}
</script>
