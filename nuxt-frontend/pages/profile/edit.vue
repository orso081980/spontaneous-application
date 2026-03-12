<template>
  <div class="max-w-2xl mx-auto">
    <NuxtLink to="/profile" class="text-indigo-600 hover:underline text-sm"> <i class="fas fa-arrow-left mr-1"></i>My Profile </NuxtLink>
    <h1 class="text-2xl font-bold text-gray-900 mt-3 mb-6">
      {{ isNew ? "Create Profile" : "Edit Profile" }}
    </h1>

    <form class="card space-y-5" @submit.prevent="submit">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <div>
          <label class="form-label">Name</label>
          <input v-model="form.name" type="text" class="form-input" />
        </div>
        <div>
          <label class="form-label">Job Position</label>
          <input v-model="form.job_position" type="text" class="form-input" />
        </div>
        <div>
          <label class="form-label">Email</label>
          <input v-model="form.email" type="email" class="form-input" />
        </div>
        <div>
          <label class="form-label">Phone</label>
          <input v-model="form.phone" type="tel" class="form-input" />
        </div>
        <div class="sm:col-span-2">
          <label class="form-label">LinkedIn URL</label>
          <input v-model="form.linkedin" type="url" class="form-input" />
        </div>
        <div class="sm:col-span-2">
          <label class="form-label">Bio</label>
          <textarea v-model="form.bio" rows="6" class="form-input" placeholder="A short introduction about yourself…"></textarea>
        </div>
      </div>

      <div v-if="error" class="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">{{ error }}</div>

      <div class="flex gap-3 justify-end">
        <NuxtLink to="/profile" class="btn-secondary">Cancel</NuxtLink>
        <button type="submit" :disabled="loading" class="btn-primary">
          <span v-if="loading"><i class="fas fa-circle-notch fa-spin mr-1"></i>Saving…</span>
          <span v-else>Save</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const api = useApi();
const router = useRouter();

// server: false → runs only on client where localStorage token is available.
// API returns a single UserProfile object (not an array), or 404 when none exists.
const { data: existing } = await useAsyncData(
  "profile-edit",
  async () => {
    try {
      return await api.get<UserProfile>("/profiles/");
    } catch {
      return null;
    }
  },
  { server: false },
);

const isNew = computed(() => !existing.value);

const form = reactive({
  name: "",
  job_position: "",
  email: "",
  phone: "",
  linkedin: "",
  bio: "",
});

// Populate form once data has loaded client-side
watch(
  existing,
  (profile) => {
    if (profile) {
      form.name = profile.name ?? "";
      form.job_position = profile.job_position ?? "";
      form.email = profile.email ?? "";
      form.phone = profile.phone ?? "";
      form.linkedin = profile.linkedin ?? "";
      form.bio = profile.bio ?? "";
    }
  },
  { immediate: true },
);

const loading = ref(false);
const error = ref<string | null>(null);

async function submit() {
  loading.value = true;
  error.value = null;
  try {
    if (isNew.value) {
      await api.post("/profiles/", form);
    } else {
      await api.put(`/profiles/${existing.value!.id}/`, form);
    }
    router.push("/profile");
  } catch {
    error.value = "Failed to save profile. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>
