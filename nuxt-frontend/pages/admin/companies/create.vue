<template>
  <div class="max-w-3xl mx-auto">
    <NuxtLink to="/companies" class="text-indigo-600 hover:underline text-sm"> <i class="fas fa-arrow-left mr-1"></i>Companies </NuxtLink>
    <h1 class="text-2xl font-bold text-gray-900 mt-3 mb-6">Add Company</h1>
    <CompanyForm :loading="loading" :error="error" @submit="submit" />
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "admin" });

const api = useApi();
const router = useRouter();
const loading = ref(false);
const error = ref<string | null>(null);

async function submit(data: Partial<Company>) {
  loading.value = true;
  error.value = null;
  try {
    const created = await api.post<Company>("/companies/", data);
    router.push(`/companies/${created.id}`);
  } catch {
    error.value = "Failed to create company. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>
