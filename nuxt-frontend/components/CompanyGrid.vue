<!-- Shared company grid used on both home and companies pages. -->
<template>
  <div>
    <!-- Loading skeleton -->
    <div v-if="pending" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="n in pageSize || 9" :key="n" class="card animate-pulse">
        <div class="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
        <div class="h-4 bg-gray-100 rounded w-1/2"></div>
      </div>
    </div>

    <!-- Company cards -->
    <div v-else-if="companies.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <NuxtLink v-for="company in companies" :key="company.id" :to="`/companies/${company.id}`" class="card hover:shadow-md transition-shadow group">
        <div class="flex items-start gap-4">
          <img
            v-if="company.logo_url"
            :src="company.logo_url"
            :alt="company.name"
            class="w-12 h-12 object-contain rounded-md border border-gray-100 flex-shrink-0"
            @error="(e) => ((e.target as HTMLImageElement).style.display = 'none')"
          />
          <div class="min-w-0 flex-1">
            <h2 class="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors truncate">
              {{ company.name }}
            </h2>
            <p class="text-sm text-gray-500 mt-0.5">{{ company.field }}</p>
            <p v-if="company.address" class="text-xs text-gray-400 mt-1 truncate"> <i class="fas fa-map-marker-alt mr-1"></i>{{ company.address }} </p>

            <!-- Tech icons: ClientOnly prevents SSR/client child-count mismatch.
                 SSR renders plain text badges; client renders icon+fallback. -->
            <div v-if="company.technologies" class="flex flex-wrap gap-1 mt-2">
              <ClientOnly>
                <!-- Client: icon with text fallback on @error -->
                <span
                  v-for="tech in splitTechs(company.technologies)"
                  :key="tech"
                  class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-700 cursor-help"
                  :title="tech"
                >
                  <img
                    :src="iconUrl(tech)"
                    :alt="tech"
                    class="w-3.5 h-3.5"
                    @error="
                      (e) => {
                        const img = e.target as HTMLImageElement;
                        img.style.display = 'none';
                        (img.nextElementSibling as HTMLElement)?.removeAttribute('style');
                      }
                    "
                  />
                  <span style="display: none">{{ tech }}</span>
                </span>
                <!-- SSR fallback: plain text badges only (no icon, no display:none) -->
                <template #fallback>
                  <span
                    v-for="tech in splitTechs(company.technologies)"
                    :key="tech"
                    class="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-700 cursor-help"
                    :title="tech"
                    >{{ tech }}</span
                  >
                </template>
              </ClientOnly>
            </div>

            <!-- Social mini-icons — @click.prevent stops the NuxtLink navigation -->
            <div class="flex gap-2 mt-2 text-gray-400" @click.prevent>
              <a v-if="company.contact" :href="`mailto:${company.contact}`" class="hover:text-indigo-600" title="Email">
                <i class="fas fa-envelope text-xs"></i>
              </a>
              <a v-if="company.linkedin_url" :href="company.linkedin_url" target="_blank" class="hover:text-blue-600" title="LinkedIn">
                <i class="fab fa-linkedin text-xs"></i>
              </a>
              <a v-if="company.twitter_url" :href="company.twitter_url" target="_blank" class="hover:text-sky-500" title="Twitter">
                <i class="fab fa-twitter text-xs"></i>
              </a>
              <a v-if="company.facebook_url" :href="company.facebook_url" target="_blank" class="hover:text-blue-700" title="Facebook">
                <i class="fab fa-facebook text-xs"></i>
              </a>
              <a v-if="company.instagram_url" :href="company.instagram_url" target="_blank" class="hover:text-pink-500" title="Instagram">
                <i class="fab fa-instagram text-xs"></i>
              </a>
              <a v-if="company.youtube_url" :href="company.youtube_url" target="_blank" class="hover:text-red-600" title="YouTube">
                <i class="fab fa-youtube text-xs"></i>
              </a>
            </div>

            <!-- App status badge — no ClientOnly needed:
                 appStatusMap starts as empty Map on SSR so v-if is always false during SSR,
                 preventing hydration mismatch. Badge appears after userApps lazy-loads. -->
            <div v-if="appStatusMap?.get(company.id)" class="mt-2">
              <span class="inline-block px-2 py-0.5 rounded-full text-xs font-medium" :class="statusBadgeClass(appStatusMap.get(company.id) ?? '')">
                {{ statusLabel(appStatusMap.get(company.id) ?? "") }}
              </span>
            </div>
          </div>
        </div>
      </NuxtLink>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-16 text-gray-400">
      <i class="fas fa-search text-4xl mb-3 block"></i>
      No companies match your search.
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  companies: Company[];
  pending?: boolean;
  pageSize?: number;
  appStatusMap?: Map<string, string>;
}>();

const { iconUrl, splitTechs } = useTechIcons();
const { statusLabel, statusBadgeClass } = useApplicationStatus();
</script>
