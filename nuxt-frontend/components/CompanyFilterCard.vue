<!--
  Composite filter card: composes SearchInput, CountryFilter, and StatusFilter.
  Logic-free: delegates each filter concern to its atomic child component.
  Emits aggregate "search" and "clear" events consumed by the parent page.
-->
<template>
  <div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Filter Companies</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <SearchInput
        :model-value="search"
        label="Search by name or field"
        placeholder="Search name or field…"
        @update:model-value="emit('update:search', $event)"
        @commit="emit('search')"
      />

      <CountryFilter :model-value="country" :countries="countries" @update:model-value="onCountryChange" />

      <StatusFilter :model-value="statusFilter" :show="showStatusFilter" @update:model-value="onStatusChange" />
    </div>

    <!-- Info row -->
    <div class="mt-4 flex flex-wrap justify-between items-center gap-2">
      <p class="text-sm text-gray-600">
        Showing {{ totalShowing }} companies
        <span v-if="totalPages && totalPages > 1"> (Page {{ currentPage }} of {{ totalPages }}) </span>
      </p>
      <button type="button" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium" @click="onClear"> Clear Filters </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  search: string;
  country: string;
  statusFilter: string;
  countries: CountryItem[];
  totalShowing: number;
  currentPage?: number;
  totalPages?: number;
  showStatusFilter: boolean;
}>();

const emit = defineEmits<{
  "update:search": [value: string];
  "update:country": [value: string];
  "update:statusFilter": [value: string];
  /** Fired after debounce (text input) or immediately (selects) */
  search: [];
  clear: [];
}>();

function onCountryChange(value: string) {
  emit("update:country", value);
  emit("search");
}

function onStatusChange(value: string) {
  emit("update:statusFilter", value);
  emit("search");
}

function onClear() {
  emit("update:search", "");
  emit("update:country", "");
  emit("update:statusFilter", "");
  emit("clear");
  emit("search");
}
</script>
