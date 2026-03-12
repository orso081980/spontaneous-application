<!--
  Atomic: application status dropdown.
  Wrapped in <ClientOnly> because visibility depends on auth state which is
  unavailable on the server (localStorage). This prevents hydration mismatches.
-->
<template>
  <ClientOnly>
    <div v-if="show">
      <label class="block text-sm font-medium text-gray-700 mb-1"> Filter by application status </label>
      <select :value="modelValue" class="form-input" @change="onChange">
        <option value="">All Statuses</option>
        <option v-if="showNotApplied !== false" value="not-applied">Not Applied</option>
        <option value="created">Created</option>
        <option value="sent">Sent</option>
        <option value="interview">Interview Stage</option>
        <option value="accepted">Accepted</option>
        <option value="refused">Refused</option>
      </select>
    </div>
    <!-- Placeholder keeps the grid column width when hidden -->
    <div v-else></div>
    <template #fallback><div></div></template>
  </ClientOnly>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string;
  /** Only render when the user is authenticated. */
  show?: boolean;
  /** Whether to include the "Not Applied" option (relevant for companies, not applications). */
  showNotApplied?: boolean;
}>();

const emit = defineEmits<{ "update:modelValue": [value: string] }>();

function onChange(e: Event) {
  emit("update:modelValue", (e.target as HTMLSelectElement).value);
}
</script>
