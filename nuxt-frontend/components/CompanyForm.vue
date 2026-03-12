<template>
  <form class="card space-y-6" @submit.prevent="$emit('submit', form)">
    <!-- Basic info -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
      <div class="sm:col-span-2">
        <label class="form-label">Company name *</label>
        <input v-model="form.name" type="text" required class="form-input" />
      </div>
      <div>
        <label class="form-label">Field / Industry *</label>
        <input v-model="form.field" type="text" required class="form-input" />
      </div>
      <div>
        <label class="form-label">Website</label>
        <input v-model="form.website" type="url" class="form-input" />
      </div>
      <div class="sm:col-span-2">
        <label class="form-label">Address</label>
        <input v-model="form.address" type="text" class="form-input" placeholder="Kerkstraat 106, 9050 Gent, Belgium" />
        <p class="mt-1 text-xs text-gray-400"
          >Format: <span class="font-mono">Street, City PostalCode, Country</span> — three comma-separated parts. City and country are saved automatically.</p
        >
      </div>
      <div>
        <label class="form-label">Contact email</label>
        <input v-model="form.contact" type="email" class="form-input" />
      </div>
      <div>
        <label class="form-label">Contact form URL</label>
        <input v-model="form.contact_form_url" type="url" class="form-input" />
      </div>
      <div>
        <label class="form-label">Phone</label>
        <input v-model="form.phone" type="tel" class="form-input" />
      </div>
      <div>
        <label class="form-label">VAT number</label>
        <input v-model="form.vat_number" type="text" class="form-input" />
      </div>
      <div>
        <label class="form-label">Logo URL</label>
        <input v-model="form.logo_url" type="url" class="form-input" />
      </div>
      <div>
        <label class="form-label">Plus Code (Google Maps)</label>
        <input v-model="form.plus_code" type="text" class="form-input" placeholder="e.g. 9F2P+2G Brussels" />
      </div>
      <div>
        <label class="form-label">Latitude</label>
        <input v-model="form.latitude" type="text" class="form-input" placeholder="50.8503" />
      </div>
      <div>
        <label class="form-label">Longitude</label>
        <input v-model="form.longitude" type="text" class="form-input" placeholder="4.3517" />
      </div>
      <div class="sm:col-span-2">
        <label class="form-label">Technologies (comma-separated)</label>
        <input v-model="form.technologies" type="text" class="form-input" placeholder="Vue.js, Django, PostgreSQL" />
      </div>
    </div>

    <!-- Social links -->
    <div>
      <h3 class="text-sm font-semibold text-gray-700 mb-3">Social links</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <div>
          <label class="form-label">LinkedIn</label>
          <input v-model="form.linkedin_url" type="url" class="form-input" />
        </div>
        <div>
          <label class="form-label">Twitter / X</label>
          <input v-model="form.twitter_url" type="url" class="form-input" />
        </div>
        <div>
          <label class="form-label">Facebook</label>
          <input v-model="form.facebook_url" type="url" class="form-input" />
        </div>
        <div>
          <label class="form-label">Instagram</label>
          <input v-model="form.instagram_url" type="url" class="form-input" />
        </div>
        <div>
          <label class="form-label">YouTube</label>
          <input v-model="form.youtube_url" type="url" class="form-input" />
        </div>
      </div>
    </div>

    <!-- Rich text fields -->
    <div>
      <label class="form-label">Description</label>
      <ClientOnly>
        <QuillEditor v-model="form.description" />
        <template #fallback>
          <textarea v-model="form.description" rows="5" class="form-input"></textarea>
        </template>
      </ClientOnly>
    </div>
    <div>
      <label class="form-label">Potential improvement</label>
      <ClientOnly>
        <QuillEditor v-model="form.potential_improvement" />
        <template #fallback>
          <textarea v-model="form.potential_improvement" rows="5" class="form-input"></textarea>
        </template>
      </ClientOnly>
    </div>

    <div v-if="error" class="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">{{ error }}</div>

    <div class="flex gap-3 justify-end">
      <button type="button" class="btn-secondary" @click="$router.back()">Cancel</button>
      <button type="submit" :disabled="loading" class="btn-primary">
        <span v-if="loading"><i class="fas fa-circle-notch fa-spin mr-1"></i>Saving…</span>
        <span v-else>Save company</span>
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
const props = defineProps<{
  initial?: Partial<Company>;
  loading?: boolean;
  error?: string | null;
}>();

defineEmits<{ submit: [data: Partial<Company>] }>();

const form = reactive<Partial<Company>>({
  name: props.initial?.name ?? "",
  field: props.initial?.field ?? "",
  website: props.initial?.website ?? "",
  address: props.initial?.address ?? "",
  contact: props.initial?.contact ?? "",
  contact_form_url: props.initial?.contact_form_url ?? "",
  phone: props.initial?.phone ?? "",
  vat_number: props.initial?.vat_number ?? "",
  logo_url: props.initial?.logo_url ?? "",
  plus_code: props.initial?.plus_code ?? "",
  latitude: props.initial?.latitude ?? "",
  longitude: props.initial?.longitude ?? "",
  technologies: props.initial?.technologies ?? "",
  linkedin_url: props.initial?.linkedin_url ?? "",
  twitter_url: props.initial?.twitter_url ?? "",
  facebook_url: props.initial?.facebook_url ?? "",
  instagram_url: props.initial?.instagram_url ?? "",
  youtube_url: props.initial?.youtube_url ?? "",
  description: props.initial?.description ?? "",
  potential_improvement: props.initial?.potential_improvement ?? "",
});
</script>
