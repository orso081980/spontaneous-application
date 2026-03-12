<template>
  <div v-if="company">
    <!-- Header -->
    <div class="flex flex-wrap items-start gap-6 mb-8">
      <img
        v-if="company.logo_url"
        :src="company.logo_url"
        :alt="company.name"
        class="w-20 h-20 object-contain rounded-lg border border-gray-200 p-1"
        @error="(e) => ((e.target as HTMLImageElement).style.display = 'none')"
      />
      <div class="flex-1 min-w-0">
        <div class="flex flex-wrap items-center gap-3">
          <h1 class="text-3xl font-bold text-gray-900">{{ company.name }}</h1>
          <div class="flex gap-2 flex-wrap">
            <a v-if="company.linkedin_url" :href="company.linkedin_url" target="_blank" class="text-blue-600 hover:text-blue-800" title="LinkedIn">
              <i class="fab fa-linkedin text-xl"></i>
            </a>
            <a v-if="company.twitter_url" :href="company.twitter_url" target="_blank" class="text-sky-500 hover:text-sky-700" title="Twitter">
              <i class="fab fa-twitter text-xl"></i>
            </a>
            <a v-if="company.facebook_url" :href="company.facebook_url" target="_blank" class="text-blue-700 hover:text-blue-900" title="Facebook">
              <i class="fab fa-facebook text-xl"></i>
            </a>
            <a v-if="company.instagram_url" :href="company.instagram_url" target="_blank" class="text-pink-500 hover:text-pink-700" title="Instagram">
              <i class="fab fa-instagram text-xl"></i>
            </a>
            <a v-if="company.youtube_url" :href="company.youtube_url" target="_blank" class="text-red-500 hover:text-red-700" title="YouTube">
              <i class="fab fa-youtube text-xl"></i>
            </a>
            <a v-if="company.contact" :href="`mailto:${company.contact}`" class="text-gray-500 hover:text-indigo-600" :title="company.contact">
              <i class="fas fa-envelope text-xl"></i>
            </a>
          </div>
        </div>
        <p class="text-gray-500 mt-1">{{ company.field }}</p>
        <p class="text-gray-400 text-sm mt-1"><i class="fas fa-map-marker-alt mr-1"></i>{{ company.address }}</p>
      </div>

      <!-- Actions -->
      <div class="flex flex-wrap gap-2">
        <a v-if="company.website" :href="company.website" target="_blank" class="btn-secondary text-sm">
          <i class="fas fa-external-link-alt mr-1"></i>Website
        </a>
        <ClientOnly>
          <div>
            <template v-if="auth.isAuthenticated">
              <!-- Already applied → show status badge + link to applications -->
              <template v-if="existingApplication">
                <NuxtLink
                  to="/applications"
                  :class="statusBtnClass(existingApplication.status)"
                  class="text-sm px-3 py-1.5 rounded-md font-medium inline-flex items-center gap-1.5"
                >
                  <i class="fas fa-check-circle"></i>
                  Applied · {{ statusLabel(existingApplication.status) }}
                </NuxtLink>
              </template>
              <template v-else>
                <NuxtLink :to="`/companies/${company.id}/apply`" class="btn-primary text-sm"> <i class="fas fa-paper-plane mr-1"></i>Apply </NuxtLink>
              </template>
            </template>
          </div>
          <template #fallback><div></div></template>
        </ClientOnly>
        <template v-if="auth.isAdmin">
          <NuxtLink :to="`/admin/companies/${company.id}/edit`" class="btn-secondary text-sm"> <i class="fas fa-edit mr-1"></i>Edit </NuxtLink>
          <button class="btn-danger text-sm" @click="confirmDelete = true"> <i class="fas fa-trash mr-1"></i>Delete </button>
        </template>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main info -->
      <div class="lg:col-span-2 space-y-6">
        <div v-if="company.description" class="card">
          <h2 class="font-semibold text-gray-900 mb-3">About</h2>
          <div class="prose prose-sm max-w-none text-gray-700" v-html="company.description"></div>
        </div>
        <div v-if="company.potential_improvement" class="card">
          <h2 class="font-semibold text-gray-900 mb-3">Potential improvement</h2>
          <div class="prose prose-sm max-w-none text-gray-700" v-html="company.potential_improvement"></div>
        </div>
        <div v-if="company.technologies" class="card">
          <h2 class="font-semibold text-gray-900 mb-3">Technologies</h2>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="tech in splitTechs(company.technologies)"
              :key="tech"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm bg-gray-100 text-gray-800 border border-gray-200 cursor-help"
              :title="tech"
            >
              <img :src="iconUrl(tech)" :alt="tech" class="w-4 h-4" @error="(e) => ((e.target as HTMLImageElement).style.display = 'none')" />
              {{ tech }}
            </span>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-4">
        <div class="card text-sm space-y-3">
          <div v-if="company.contact">
            <p class="form-label">Contact</p>
            <a :href="`mailto:${company.contact}`" class="text-indigo-600 hover:underline">{{ company.contact }}</a>
          </div>
          <div v-if="company.phone">
            <p class="form-label">Phone</p>
            <p>{{ company.phone }}</p>
          </div>
          <div v-if="company.vat_number">
            <p class="form-label">VAT</p>
            <p>{{ company.vat_number }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete confirm modal -->
    <div v-if="confirmDelete" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="card max-w-sm w-full mx-4">
        <h3 class="font-semibold text-lg text-gray-900 mb-2">Delete company?</h3>
        <p class="text-gray-600 text-sm mb-5">This action cannot be undone.</p>
        <div class="flex gap-3 justify-end">
          <button class="btn-secondary" @click="confirmDelete = false">Cancel</button>
          <button class="btn-danger" :disabled="deleting" @click="deleteCompany">
            <span v-if="deleting"><i class="fas fa-circle-notch fa-spin mr-1"></i>Deleting…</span>
            <span v-else>Delete</span>
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="error" class="text-center py-20 text-red-500">
    <i class="fas fa-exclamation-circle text-4xl mb-3 block"></i>
    Company not found.
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const api = useApi();
const { iconUrl, splitTechs } = useTechIcons();
const { statusLabel, statusBtnClass } = useApplicationStatus();

const { data: company, error } = await useAsyncData(`company-${route.params.id}`, () => api.get<Company>(`/companies/${route.params.id}/`));

const existingApplication = ref<JobApplication | null>(null);

onMounted(async () => {
  if (auth.isAuthenticated) {
    try {
      const apps = await api.get<JobApplication[]>("/applications/");
      existingApplication.value = (apps ?? []).find((a: JobApplication) => a.company_id === route.params.id) ?? null;
    } catch {
      /* no profile or not logged in */
    }
  }
});

const confirmDelete = ref(false);
const deleting = ref(false);

async function deleteCompany() {
  deleting.value = true;
  try {
    await api.del(`/companies/${route.params.id}/`);
    router.push("/companies");
  } finally {
    deleting.value = false;
    confirmDelete.value = false;
  }
}
</script>
