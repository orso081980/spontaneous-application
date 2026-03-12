<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">My Profile</h1>
      <NuxtLink to="/profile/edit" class="btn-primary"> <i class="fas fa-edit mr-2"></i>Edit </NuxtLink>
    </div>

    <div v-if="profile" class="card space-y-5">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <div>
          <p class="form-label">Name</p>
          <p class="mt-1 text-gray-900">{{ profile.name || "—" }}</p>
        </div>
        <div>
          <p class="form-label">Job Position</p>
          <p class="mt-1 text-gray-900">{{ profile.job_position || "—" }}</p>
        </div>
        <div>
          <p class="form-label">Email</p>
          <p class="mt-1 text-gray-900">{{ profile.email || "—" }}</p>
        </div>
        <div>
          <p class="form-label">Phone</p>
          <p class="mt-1 text-gray-900">{{ profile.phone || "—" }}</p>
        </div>
        <div v-if="profile.linkedin" class="sm:col-span-2">
          <p class="form-label">LinkedIn</p>
          <a :href="profile.linkedin" target="_blank" class="text-indigo-600 hover:underline">{{ profile.linkedin }}</a>
        </div>
        <div v-if="profile.bio" class="sm:col-span-2">
          <p class="form-label">Bio</p>
          <div class="prose prose-sm max-w-none mt-1" v-html="profile.bio"></div>
        </div>
      </div>
    </div>

    <div v-else-if="!pending" class="text-center py-16">
      <p class="text-gray-500 mb-4">You don't have a profile yet.</p>
      <NuxtLink to="/profile/edit" class="btn-primary">Create Profile</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const api = useApi();
// server: false → runs only on client where localStorage token is available.
// API returns a single UserProfile object (not an array), or 404 when none exists.
const { data: profile, pending } = await useAsyncData(
  "my-profile",
  async () => {
    try {
      return await api.get<UserProfile>("/profiles/");
    } catch {
      return null;
    }
  },
  { server: false },
);
</script>
