<template>
  <div class="max-w-md mx-auto mt-12">
    <div class="card">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Sign in</h1>

      <form @submit.prevent="submit" class="space-y-5">
        <div>
          <label class="form-label" for="username">Username</label>
          <input id="username" v-model="form.username" type="text" required autocomplete="username" class="form-input" />
        </div>

        <div>
          <label class="form-label" for="password">Password</label>
          <input id="password" v-model="form.password" type="password" required autocomplete="current-password" class="form-input" />
        </div>

        <div v-if="error" class="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          {{ error }}
        </div>

        <button type="submit" :disabled="loading" class="btn-primary w-full justify-center flex">
          <span v-if="loading"><i class="fas fa-circle-notch fa-spin mr-2"></i>Signing in…</span>
          <span v-else>Sign in</span>
        </button>
      </form>

      <p class="mt-4 text-sm text-gray-600 text-center">
        Don't have an account?
        <NuxtLink to="/register" class="text-indigo-600 hover:underline">Register</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "default" });

const { login, error, loading } = useAuth();

const form = reactive({ username: "", password: "" });

async function submit() {
  await login(form.username, form.password);
}
</script>
