<template>
  <div class="min-h-screen flex flex-col">
    <!-- Navbar -->
    <nav class="bg-indigo-600 shadow-md">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <NuxtLink to="/" class="flex items-center gap-2 text-white font-bold text-xl">
            <i class="fas fa-bolt"></i>
            Spontaneous
          </NuxtLink>

          <!-- Nav links -->
          <div class="hidden md:flex items-center gap-6 text-sm font-medium text-indigo-100">
            <NuxtLink to="/companies" class="hover:text-white transition-colors">Companies</NuxtLink>
            <NuxtLink to="/companies/map" class="hover:text-white transition-colors">Map</NuxtLink>
            <!-- ClientOnly prevents SSR/CSR hydration mismatch (auth lives in localStorage) -->
            <ClientOnly>
              <template v-if="auth.isAuthenticated">
                <NuxtLink to="/applications" class="hover:text-white transition-colors">My Applications</NuxtLink>
                <NuxtLink to="/profile" class="hover:text-white transition-colors">Profile</NuxtLink>
                <template v-if="auth.isAdmin">
                  <NuxtLink to="/admin/companies/create" class="hover:text-white transition-colors"> <i class="fas fa-plus-circle"></i> Add Company </NuxtLink>
                </template>
                <button @click="handleLogout" class="hover:text-white transition-colors">Logout</button>
              </template>
              <template v-else>
                <NuxtLink to="/login" class="hover:text-white transition-colors">Login</NuxtLink>
                <NuxtLink to="/register" class="bg-white text-indigo-600 hover:bg-indigo-50 px-3 py-1.5 rounded-md transition-colors">Register</NuxtLink>
              </template>
              <template #fallback>
                <NuxtLink to="/login" class="hover:text-white transition-colors">Login</NuxtLink>
                <NuxtLink to="/register" class="bg-white text-indigo-600 hover:bg-indigo-50 px-3 py-1.5 rounded-md transition-colors">Register</NuxtLink>
              </template>
            </ClientOnly>
          </div>

          <!-- Mobile menu button -->
          <button class="md:hidden text-white focus:outline-none" @click="mobileOpen = !mobileOpen">
            <i :class="mobileOpen ? 'fas fa-times' : 'fas fa-bars'" class="text-xl"></i>
          </button>
        </div>
      </div>

      <!-- Mobile menu -->
      <div v-if="mobileOpen" class="md:hidden bg-indigo-700 px-4 pb-4 space-y-2 text-sm text-indigo-100">
        <NuxtLink to="/companies" class="block py-1 hover:text-white" @click="mobileOpen = false">Companies</NuxtLink>
        <NuxtLink to="/companies/map" class="block py-1 hover:text-white" @click="mobileOpen = false">Map</NuxtLink>
        <ClientOnly>
          <template v-if="auth.isAuthenticated">
            <NuxtLink to="/applications" class="block py-1 hover:text-white" @click="mobileOpen = false">My Applications</NuxtLink>
            <NuxtLink to="/profile" class="block py-1 hover:text-white" @click="mobileOpen = false">Profile</NuxtLink>
            <button class="block py-1 hover:text-white w-full text-left" @click="handleLogout">Logout</button>
          </template>
          <template v-else>
            <NuxtLink to="/login" class="block py-1 hover:text-white" @click="mobileOpen = false">Login</NuxtLink>
            <NuxtLink to="/register" class="block py-1 hover:text-white" @click="mobileOpen = false">Register</NuxtLink>
          </template>
          <template #fallback>
            <NuxtLink to="/login" class="block py-1 hover:text-white" @click="mobileOpen = false">Login</NuxtLink>
            <NuxtLink to="/register" class="block py-1 hover:text-white" @click="mobileOpen = false">Register</NuxtLink>
          </template>
        </ClientOnly>
      </div>
    </nav>

    <!-- Main content -->
    <main class="flex-1">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <slot />
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 text-center text-sm text-gray-500"> © {{ new Date().getFullYear() }} Spontaneous Job Board </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore();
const { logout } = useAuth();
const mobileOpen = ref(false);

async function handleLogout() {
  mobileOpen.value = false;
  await logout();
}
</script>
