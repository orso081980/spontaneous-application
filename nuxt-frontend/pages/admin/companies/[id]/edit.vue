<template>
  <div class="max-w-3xl mx-auto">
    <NuxtLink :to="`/companies/${route.params.id}`" class="text-indigo-600 hover:underline text-sm">
      <i class="fas fa-arrow-left mr-1"></i>Back to company
    </NuxtLink>
    <h1 class="text-2xl font-bold text-gray-900 mt-3 mb-6">Edit Company</h1>
    <CompanyForm v-if="company" :initial="company" :loading="loading" :error="error" @submit="submit" />
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "admin" });

const route = useRoute();
const router = useRouter();
const api = useApi();

const { data: company } = await useAsyncData(`company-edit-${route.params.id}`, () => api.get<Company>(`/companies/${route.params.id}/`));

const loading = ref(false);
const error = ref<string | null>(null);

async function submit(data: Partial<Company>) {
  loading.value = true;
  error.value = null;
  try {
    await api.put(`/companies/${route.params.id}/`, data);
    router.push(`/companies/${route.params.id}`);
  } catch {
    error.value = "Failed to update company. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>
