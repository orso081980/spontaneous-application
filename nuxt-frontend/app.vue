<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
const authStore = useAuthStore();
// Rehydrate token/user from localStorage — only runs on the client.
// Moving this into onMounted avoids any SSR context confusion in Nuxt 4.
onMounted(() => {
  authStore.init();
});
</script>
