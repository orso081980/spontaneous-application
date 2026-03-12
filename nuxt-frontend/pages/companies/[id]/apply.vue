<template>
  <div class="max-w-2xl mx-auto">
    <div v-if="company" class="mb-6">
      <NuxtLink :to="`/companies/${route.params.id}`" class="text-indigo-600 hover:underline text-sm">
        <i class="fas fa-arrow-left mr-1"></i>Back to {{ company.name }}
      </NuxtLink>
      <h1 class="text-2xl font-bold text-gray-900 mt-3">Apply to {{ company.name }}</h1>
    </div>

    <form class="card space-y-5" @submit.prevent="submit">
      <div>
        <label class="form-label">Position</label>
        <input v-model="form.position" type="text" required class="form-input" placeholder="e.g. Frontend Developer" />
      </div>
      <div>
        <label class="form-label">Project to suggest</label>
        <ClientOnly>
          <QuillEditor v-model="form.project_to_suggest" />
          <template #fallback>
            <textarea v-model="form.project_to_suggest" rows="4" class="form-input" placeholder="Brief project idea"></textarea>
          </template>
        </ClientOnly>
      </div>
      <div>
        <label class="form-label">Link to project</label>
        <input v-model="form.link_to_project" type="url" class="form-input" placeholder="https://github.com/…" />
      </div>
      <div>
        <label class="form-label">Message</label>
        <ClientOnly>
          <QuillEditor v-model="form.message" />
          <template #fallback>
            <textarea v-model="form.message" rows="5" class="form-input" placeholder="Introduce yourself…"></textarea>
          </template>
        </ClientOnly>
      </div>

      <div v-if="error" class="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">{{ error }}</div>

      <div class="flex gap-3 justify-end">
        <NuxtLink :to="`/companies/${route.params.id}`" class="btn-secondary">Cancel</NuxtLink>
        <button type="submit" :disabled="loading" class="btn-primary">
          <span v-if="loading"><i class="fas fa-circle-notch fa-spin mr-1"></i>Sending…</span>
          <span v-else><i class="fas fa-paper-plane mr-1"></i>Submit application</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const route = useRoute();
const router = useRouter();
const api = useApi();

const { data: company } = await useAsyncData(`company-apply-${route.params.id}`, () => api.get<Company>(`/companies/${route.params.id}/`));

const form = reactive({
  position: "",
  project_to_suggest: "",
  link_to_project: "",
  message: "",
});
const loading = ref(false);
const error = ref<string | null>(null);

async function submit() {
  loading.value = true;
  error.value = null;
  try {
    await api.post("/applications/", {
      ...form,
      company_id: route.params.id,
    });
    router.push("/applications");
  } catch (e: unknown) {
    error.value = "Failed to submit application. Please try again.";
    console.error(e);
  } finally {
    loading.value = false;
  }
}
</script>
