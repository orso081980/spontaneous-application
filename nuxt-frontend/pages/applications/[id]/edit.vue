<template>
  <div class="max-w-2xl mx-auto">
    <NuxtLink to="/applications" class="text-indigo-600 hover:underline text-sm"> <i class="fas fa-arrow-left mr-1"></i>My Applications </NuxtLink>

    <h1 class="text-2xl font-bold text-gray-900 mt-3 mb-6">Edit Application</h1>

    <form v-if="form" class="card space-y-5" @submit.prevent="submit">
      <div>
        <label class="form-label">Position</label>
        <input v-model="form.position" type="text" required class="form-input" />
      </div>
      <div>
        <label class="form-label">Status</label>
        <select v-model="form.status" class="form-input">
          <option value="created">Created</option>
          <option value="sent">Sent</option>
          <option value="interview">Interview</option>
          <option value="accepted">Accepted</option>
          <option value="refused">Refused</option>
        </select>
      </div>
      <div>
        <label class="form-label">Project to suggest</label>
        <ClientOnly>
          <QuillEditor v-model="form.project_to_suggest" />
          <template #fallback>
            <textarea v-model="form.project_to_suggest" rows="4" class="form-input"></textarea>
          </template>
        </ClientOnly>
      </div>
      <div>
        <label class="form-label">Link to project</label>
        <input v-model="form.link_to_project" type="url" class="form-input" />
      </div>
      <div>
        <label class="form-label">Message</label>
        <ClientOnly>
          <QuillEditor v-model="form.message" />
          <template #fallback>
            <textarea v-model="form.message" rows="5" class="form-input"></textarea>
          </template>
        </ClientOnly>
      </div>

      <div v-if="error" class="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">{{ error }}</div>

      <div class="flex gap-3 justify-end">
        <NuxtLink to="/applications" class="btn-secondary">Cancel</NuxtLink>
        <button type="submit" :disabled="loading" class="btn-primary">
          <span v-if="loading"><i class="fas fa-circle-notch fa-spin mr-1"></i>Saving…</span>
          <span v-else>Save changes</span>
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

const { data: app } = await useAsyncData(`app-edit-${route.params.id}`, () => api.get<JobApplication>(`/applications/${route.params.id}/`));

const form = reactive({
  position: app.value?.position ?? "",
  status: app.value?.status ?? "created",
  project_to_suggest: app.value?.project_to_suggest ?? "",
  link_to_project: app.value?.link_to_project ?? "",
  message: app.value?.message ?? "",
});

const loading = ref(false);
const error = ref<string | null>(null);

async function submit() {
  loading.value = true;
  error.value = null;
  try {
    await api.put(`/applications/${route.params.id}/`, form);
    router.push("/applications");
  } catch {
    error.value = "Failed to update application. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>
