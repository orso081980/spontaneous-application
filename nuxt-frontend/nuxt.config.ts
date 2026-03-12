// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
  ],

  css: ['~/assets/css/main.css'],

  tailwindcss: {
    cssPath: '~/assets/css/main.css',
  },

  runtimeConfig: {
    // Private keys (server-side only) — none needed for this app
    // Public keys (exposed to client-side)
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api',
      googleMapsApiKey: process.env.NUXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
      staticBase: process.env.NUXT_PUBLIC_STATIC_BASE || 'http://localhost:8000/static',
    },
  },

  // Auto-import composables and stores
  imports: {
    dirs: ['stores', 'composables'],
  },

  // App-level head config
  app: {
    head: {
      title: 'Spontaneous Job Board',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Spontaneous job application tracker' },
      ],
      link: [
        { rel: 'stylesheet', href: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css' },
        { rel: 'stylesheet', href: 'https://cdn.quilljs.com/1.3.7/quill.snow.css' },
      ],
      script: [
        { src: 'https://cdn.quilljs.com/1.3.7/quill.min.js' },
      ],
    },
  },
})
