<!-- Client-only Quill v-model wrapper. Quill is loaded from CDN in nuxt.config.ts head. -->
<template>
  <div class="quill-wrapper">
    <div ref="container"></div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ modelValue?: string }>();
const emit = defineEmits<{ "update:modelValue": [value: string] }>();

const container = ref<HTMLElement | null>(null);
let quill: QuillInstance | null = null;

onMounted(() => {
  if (!container.value) return;
  quill = new Quill(container.value, {
    theme: "snow",
    modules: {
      toolbar: [["bold", "italic", "underline"], ["link"], [{ list: "ordered" }, { list: "bullet" }], ["clean"]],
    },
  });
  if (props.modelValue) {
    quill.root.innerHTML = props.modelValue;
  }
  quill.on("text-change", () => {
    if (quill) emit("update:modelValue", quill.root.innerHTML);
  });
});

watch(
  () => props.modelValue,
  (val) => {
    if (!quill) return;
    const newVal = val ?? "";
    if (quill.root.innerHTML !== newVal) {
      quill.root.innerHTML = newVal;
    }
  },
);
</script>

<style>
.quill-wrapper .ql-toolbar {
  border-top-left-radius: 0.375rem;
  border-top-right-radius: 0.375rem;
  background: #f9fafb;
}
.quill-wrapper .ql-container {
  min-height: 180px;
  font-family: inherit;
  font-size: 0.875rem;
  border-bottom-left-radius: 0.375rem;
  border-bottom-right-radius: 0.375rem;
}
.quill-wrapper .ql-editor {
  min-height: 180px;
}
</style>
