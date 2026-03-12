# Nuxt Frontend — Architecture & Development Guide

## Stack

- **Nuxt 4** (Vue 3 Composition API, SSR enabled)
- **Pinia** for auth state
- **Tailwind CSS** for styling
- **ofetch** (`$fetch`) for HTTP calls to the Django REST API
- **Quill** (CDN) for rich-text fields

---

## Project Structure

```
composables/
  useApi.ts              — wraps $fetch with the auth token header
  useAuth.ts             — login / register / logout actions with typed errors
  useApplicationFilters  — client-side filter logic for the applications list
  useApplicationStatus   — shared statusLabel + statusClass helpers (no duplication)
  usePagination.ts       — client-side windowed pagination (shared between pages)
  useTechIcons.ts        — resolves tech names → SVG icon URLs

stores/
  auth.ts               — Pinia store: token + user, persisted in localStorage

components/
  SearchInput.vue        — atomic: debounced text input, emits update:modelValue + commit
  CountryFilter.vue      — atomic: country <select>, emits update:modelValue on change
  StatusFilter.vue       — atomic: status <select> wrapped in <ClientOnly> (auth-gated)
  CompanyFilterCard.vue  — composite wrapper: Search + Country + Status + info row
  CompanyGrid.vue        — card grid with loading skeleton, tech icons, app-status badges
  CompanyPagination.vue  — windowed page-number control (max 5 visible pages)
  CompanyForm.vue        — shared create/edit company form
  QuillEditor.vue        — thin wrapper around the Quill CDN editor

middleware/
  auth.ts               — redirects unauthenticated users to /login
  admin.ts              — additionally checks isAdmin, redirects to /

pages/
  index.vue             — home: loads all companies client-side, filters in-memory
  login.vue / register.vue
  companies/
    index.vue           — paginated company list (SSR), path-based pagination
    [id].vue            — company detail (SSR)
    map.vue             — Google Maps view
    [id]/apply.vue      — create application (auth)
    page/[n].vue        — paginated company list page N (SSR)
  applications/
    index.vue           — my applications (auth, client-side filter + pagination)
    [id]/edit.vue       — edit application (auth)
  profile/
    index.vue           — view profile (auth)
    edit.vue            — create / update profile (auth)
  admin/companies/
    create.vue          — admin: create company
    [id]/edit.vue       — admin: edit company
```

---

## Pages & Routing

| Route                       | Auth   | API Endpoint                       |
| --------------------------- | ------ | ---------------------------------- |
| `/`                         | Public | `GET /companies/`                  |
| `/companies`                | Public | `GET /companies/paginated/`        |
| `/companies/page/:n`        | Public | `GET /companies/paginated/?page=n` |
| `/companies/:id`            | Public | `GET /companies/:id/`              |
| `/companies/:id/apply`      | Auth   | `POST /applications/`              |
| `/applications`             | Auth   | `GET /applications/`               |
| `/applications/:id/edit`    | Auth   | `PUT /applications/:id/`           |
| `/profile`                  | Auth   | `GET /profiles/me/`                |
| `/profile/edit`             | Auth   | `POST`/`PUT /profiles/me/`         |
| `/admin/companies/create`   | Admin  | `POST /companies/`                 |
| `/admin/companies/:id/edit` | Admin  | `PUT /companies/:id/`              |

---

## CRUD Coverage

### Companies (admin-managed)

| Operation   | Route                       | Method                          |
| ----------- | --------------------------- | ------------------------------- |
| Create      | `/admin/companies/create`   | `POST /api/companies/`          |
| Read list   | `/companies`                | `GET /api/companies/paginated/` |
| Read detail | `/companies/:id`            | `GET /api/companies/:id/`       |
| Update      | `/admin/companies/:id/edit` | `PUT /api/companies/:id/`       |
| Delete      | button on `/companies/:id`  | `DELETE /api/companies/:id/`    |

### Applications (user-managed)

| Operation | Route                            | Method                          |
| --------- | -------------------------------- | ------------------------------- |
| Create    | `/companies/:id/apply`           | `POST /api/applications/`       |
| Read list | `/applications`                  | `GET /api/applications/`        |
| Update    | `/applications/:id/edit`         | `PUT /api/applications/:id/`    |
| Delete    | inline button in `/applications` | `DELETE /api/applications/:id/` |

### Profile (user-managed)

| Operation       | Route              | Method                         |
| --------------- | ------------------ | ------------------------------ |
| Create / Update | `/profile/edit`    | `POST`/`PUT /api/profiles/me/` |
| Read            | `/profile`         | `GET /api/profiles/me/`        |
| Delete          | ❌ not implemented | —                              |

---

## Middleware

### `auth.ts`

Applied via `definePageMeta({ middleware: 'auth' })` on every protected page.

**What it does**: Checks `authStore.isAuthenticated`. If `false`, redirects to `/login`.

**SSR caveat**: Auth state lives in `localStorage` and is rehydrated in `app.vue`'s `onMounted`. This means the Pinia store is always empty on the **server**. Nuxt only runs route middleware **client-side** (not during SSR for the initial page render), so protected pages receive their server-rendered HTML before the guard fires. On first client mount, if the user is not authenticated, they are redirected to `/login`.

### `admin.ts`

Applied on all `/admin/**` routes. Checks both `isAuthenticated` and `isAdmin`. Redirects to `/login` if not logged in, or to `/` if logged in but not admin.

---

## Composables

### `useApi`

Thin wrapper around `$fetch`. Attaches `Authorization: Token <token>` when a token exists in the Pinia store. Provides typed `get`, `post`, `put`, `del` helpers.

### `useAuth`

Handles `login`, `register`, and `logout`. Maps HTTP status codes to user-friendly error messages:

| Code    | Meaning                                   | Message shown                            |
| ------- | ----------------------------------------- | ---------------------------------------- |
| `400`   | Validation errors (field errors from DRF) | Joined field messages                    |
| `401`   | Bad credentials                           | "Invalid credentials. Please try again." |
| `409`   | Conflict (e.g. username taken)            | "Username already taken."                |
| `422`   | Unprocessable entity                      | Joined field messages                    |
| `500+`  | Server error                              | "Server error. Please try again later."  |
| Network | No response                               | "Network error. Check your connection."  |

### `usePagination`

Shared between companies (server-side result sets) and applications (client-side arrays).

```ts
const { page, totalPages, paginatedItems, visiblePages, goTo } = usePagination(itemsRef, pageSize);
```

- `paginatedItems` — computed slice of the input array for the current page
- `visiblePages` — windowed array of page numbers (max 5, centred on current page)
- `goTo(n)` — clamps and sets `page`
- Automatically resets to page 1 when `items` changes (e.g. after a filter change)

### `useApplicationStatus`

Single source of truth for status display. No more duplicated `statusLabel` / `statusClass` functions across `CompanyGrid.vue` and `applications/index.vue`.

```ts
const { statusLabel, statusClass, statusBadgeClass, statusBtnClass } = useApplicationStatus();
```

### `useApplicationFilters`

Encapsulates the client-side filter state for `/applications`.

```ts
const { search, status, filtered, clear } = useApplicationFilters(applicationsRef);
```

---

## Atomic Filter Components

**Design principle**: each component owns only one concern and nothing else.

| Component           | Concern                                     | Events                        |
| ------------------- | ------------------------------------------- | ----------------------------- |
| `SearchInput.vue`   | Text search with debounce                   | `update:modelValue`, `commit` |
| `CountryFilter.vue` | Country `<select>`                          | `update:modelValue`           |
| `StatusFilter.vue`  | Status `<select>` wrapped in `<ClientOnly>` | `update:modelValue`           |

`CompanyFilterCard.vue` is the composite that wires these three inside a card layout and owns the aggregate `@search` / `@clear` events used by the pages.

---

## SSR & Hydration

### Why hydration warnings occur

Vue SSR requires the server-rendered DOM to **exactly** match what Vue renders on the client during hydration. Any diff — even in attribute order — triggers the warning `[Vue warn]: Hydration children mismatch`.

### Root causes in this app

#### 1. Non-deterministic API ordering (home page)

`pages/index.vue` fetches **all** companies from `/api/companies/` (no pagination) via SSR. MongoDB may return documents in a different natural order on each request. SSR renders `[CompanyA, CompanyB, …]`; if the client refetches or payload is stale it gets `[CompanyB, CompanyA, …]` → different `href` in each `<NuxtLink>` → mismatch.

**Fix**: `server: false` on the home-page `useAsyncData`. Filtering is 100% client-side anyway, so SSR provides zero benefit while causing the mismatch. The initial render shows a skeleton (handled by `CompanyGrid`'s `pending` state).

#### 2. `watch` option inside `useAsyncData` (companies paginated pages)

Nuxt 4 changed how `watch` in `useAsyncData` behaves: it schedules an immediate client-side re-execute to verify parameters haven't drifted since SSR. Even when the refs have identical values, a re-fetch goes out, and if MongoDB returns a different ordering the mismatch appears.

**Fix**: Remove `watch` from `useAsyncData` and own the re-fetch with an explicit `watch()` + `refresh()` pattern:

```ts
// ✅ Correct — SSR once, re-fetch only on explicit param changes
const { data, pending, refresh } = await useAsyncData("key", fetcher);
watch([page, search, country, statusFilter], () => refresh());

// ❌ Avoid — the watch option can trigger an unintended client re-execute
const { data } = await useAsyncData("key", fetcher, { watch: [page, search] });
```

#### 3. `<ClientOnly>` with `<template v-if>` as direct child

When the direct child of `<ClientOnly>` is a `<template v-if="…">` that evaluates to nothing, the resulting DOM does not reliably match the comment node left by SSR.

**Fix**: Wrap conditional client-side content in a real element:

```html
<!-- ✅ -->
<ClientOnly>
  <div>
    <template v-if="auth.isAuthenticated">…</template>
  </div>
</ClientOnly>

<!-- ❌ -->
<ClientOnly>
  <template v-if="auth.isAuthenticated">…</template>
</ClientOnly>
```

---

## Application Status Values

| Value       | Label           | Badge colour |
| ----------- | --------------- | ------------ |
| `created`   | Created         | Grey         |
| `sent`      | Sent            | Blue         |
| `interview` | Interview Stage | Yellow       |
| `accepted`  | Accepted        | Green        |
| `refused`   | Refused         | Red          |

The `statusLabel` / `statusClass` helpers live exclusively in `useApplicationStatus` and are imported wherever a status needs to be displayed. The one-liner `status.charAt(0).toUpperCase() + status.slice(1)` pattern is **not** used because it does not handle the `interview → "Interview Stage"` label correctly.

---

## Known Limitations

- Profile **Delete** is not implemented (no API endpoint, no page).
- Map view requires a valid `NUXT_PUBLIC_GOOGLE_MAPS_API_KEY` env variable.
- Auth state is in `localStorage`; SSR always sees unauthenticated state. Middleware only redirects client-side (first mount). This is intentional — no cookie session.
- Application status filtering on the companies list disables SSR (`server: false` when a status filter is active) because the auth token is only available client-side.

---

## How SSR works in this app (and why we sometimes disable it)

### What SSR means here

**Server-Side Rendering (SSR)** means Nuxt runs your Vue component code on the Node.js server before sending _any_ HTML to the browser. The server fetches data, renders the component tree into an HTML string, and sends that to the browser.

The browser receives pre-built HTML immediately — the user sees content before any JavaScript has loaded. Once the JS bundle arrives, Vue "hydrates" the page: it takes over the server-rendered DOM without rebuilding it, and makes the page interactive.

### The SSR lifecycle in one request

```
1. Browser requests /companies
        ↓
2. Nuxt server runs setup() + useAsyncData()
   ↳ fetches /api/companies/paginated/ from Django
   ↳ data arrives → component renders to HTML string
        ↓
3. Server sends HTML + JSON payload to browser (fast first paint)
        ↓
4. Browser parses HTML → user sees the company grid immediately
        ↓
5. JS bundle loads → Vue "hydrates":
   ↳ re-runs setup() — but useAsyncData RE-USES the server payload, no new fetch
   ↳ Vue walks the real DOM and attaches event handlers
   ↳ app is now interactive
```

### Why hydration fails when server and client disagree

During step 5, Vue compares what it _expects_ to render (based on the current data) against what the server _actually_ rendered (in the HTML). If they differ — even in a single attribute or element count — Vue logs:

```
[Vue warn]: Hydration node mismatch
```

The page still works, but Vue falls back to a full client-side re-render, which can cause flicker, duplicate API calls, or broken references.

### Why `server: false` was needed — and why it is not enough alone

`server: false` tells Nuxt: _do not run this fetch on the server_. Return `null` immediately and do the fetch on the client instead.

This was added to fix a MongoDB-specific problem: MongoDB returns documents in **natural insertion order**, which can be non-deterministic across requests. If the server returns `[CompanyA, CompanyB]` and milliseconds later the client independently re-fetches and gets `[CompanyB, CompanyA]`, the `href` attributes on each `<NuxtLink>` differ → hydration mismatch.

**But `server: false` introduces a new mismatch problem:**

```
Server (server: false)         data=null, pending=false  → renders: <div class="empty-state">
Client (during hydration)      data=null, pending=true   → expects:  <div class="skeleton">
                                                                       ↑ DIFFERENT STRUCTURE
```

The server never fetched, so `pending=false` and it renders the _empty state_. The client starts the fetch, so `pending=true` and it wants to render the _skeleton_. Two different DOM shapes → hydration mismatch.

### The correct pattern: `<ClientOnly>` for purely client-side content

When data is **never fetched on the server**, the component that renders it should be wrapped in `<ClientOnly>`:

```html
<ClientOnly>
  <MyDataDrivenComponent :data="data" :pending="pending" />
  <template #fallback>
    <!-- This is what SSR renders. Use a skeleton or placeholder. -->
    <div class="card animate-pulse">…</div>
  </template>
</ClientOnly>
```

**How it works:**

| Phase           | What happens                                                           |
| --------------- | ---------------------------------------------------------------------- |
| SSR             | Renders only `<template #fallback>`. No component, no data dependency. |
| Hydration       | Vue matches the fallback HTML exactly — no mismatch possible.          |
| After hydration | `<ClientOnly>` mounts the real component. Fetches fire. UI updates.    |

The `#fallback` must render HTML that is structurally stable — it never needs to match the real component's output because Vue discards it after hydration.

### Which pages use SSR and which do not

| Page                                | SSR?                                 | Why                                                           |
| ----------------------------------- | ------------------------------------ | ------------------------------------------------------------- |
| `/companies` + `/companies/page/:n` | Yes (unless status filter active)    | Paginated list is indexable; server renders the grid          |
| `/companies/:id`                    | Yes                                  | Company detail is indexable                                   |
| `/` (home)                          | No (`<ClientOnly>` + `server:false`) | Pure in-browser filtering; MongoDB ordering not deterministic |
| `/applications`                     | No (`server:false`)                  | Auth-gated, no SEO value; token only in localStorage          |
| `/profile`                          | No                                   | Auth-gated                                                    |
| Admin pages                         | No                                   | Auth + admin-gated                                            |

### Why the `watch` option inside `useAsyncData` was removed

Nuxt 4 changed how the `watch` option in `useAsyncData` behaves: it schedules an **immediate client-side re-execute** on mount to verify whether the watched refs changed since SSR. Even when the refs are identical, a new fetch fires — and if MongoDB returns a different ordering, the DOM updates and a mismatch is logged.

The fix is to manage re-fetching manually:

```ts
// Correct: SSR once, re-fetch only when params actually change
const { data, refresh } = await useAsyncData("key", fetcher, { server: true });
watch([page, search, country], () => refresh());

// Avoid: triggers an implicit re-execute on every hydration
const { data } = await useAsyncData("key", fetcher, {
  server: true,
  watch: [page, search, country], // ← remove this
});
```
