<!-- Atomic: debounced text search input. -->
<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1">{{ label }}</label>
    <input :value="modelValue" type="text" :placeholder="placeholder" class="form-input" @input="onInput" />
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue: string;
    label?: string;
    placeholder?: string;
    /** Debounce delay in ms before the commit event fires. Default: 350. */
    debounce?: number;
  }>(),
  { label: "Search", placeholder: "Search…", debounce: 350 },
);

const emit = defineEmits<{
  "update:modelValue": [value: string];
  /** Fires after the debounce delay — parent should trigger the actual search. */
  commit: [];
}>();

let timer: ReturnType<typeof setTimeout>;

function onInput(e: Event) {
  emit("update:modelValue", (e.target as HTMLInputElement).value);
  clearTimeout(timer);
  timer = setTimeout(() => emit("commit"), props.debounce);
}

onUnmounted(() => clearTimeout(timer));
</script>
