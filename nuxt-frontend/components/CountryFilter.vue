<!-- Atomic: country dropdown filter. -->
<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1">Filter by country</label>
    <select :value="modelValue" class="form-input" @change="onChange">
      <option value="">All countries</option>
      <option v-for="c in countries" :key="c.name" :value="c.name"> {{ c.flag }} {{ c.name }} </option>
    </select>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string;
  countries: CountryItem[];
}>();

const emit = defineEmits<{ "update:modelValue": [value: string] }>();

function onChange(e: Event) {
  emit("update:modelValue", (e.target as HTMLSelectElement).value);
}
</script>
