// Quill editor — loaded from CDN (quill.min.js in head)
declare interface QuillInstance {
  root: { innerHTML: string }
  on(event: string, handler: () => void): void
}
declare const Quill: new (el: HTMLElement, options: object) => QuillInstance

declare interface Company {
  id: string
  name: string
  field: string
  website: string
  address: string
  contact: string
  contact_form_url: string
  phone: string
  vat_number: string
  description: string
  potential_improvement: string
  logo_url: string
  plus_code: string
  latitude: string
  longitude: string
  technologies: string
  linkedin_url: string
  facebook_url: string
  twitter_url: string
  instagram_url: string
  youtube_url: string
  created_at: string
  updated_at: string
}

declare interface UserProfile {
  id: string
  user_id: number
  username: string
  name: string
  job_position: string
  email: string
  phone: string
  bio: string
  linkedin: string
  created_at: string
  updated_at: string
}

declare interface JobApplication {
  id: string
  company_id: string
  company_name: string
  user_profile_id: string
  position: string
  project_to_suggest: string
  link_to_project: string
  message: string
  status: 'created' | 'sent' | 'interview' | 'accepted' | 'refused'
  created_at: string
  updated_at: string
}

// Standard DRF paginated response (unused — keep for reference)
declare interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Actual shape returned by /api/companies/paginated/
declare interface CompaniesApiResponse {
  results: Company[]
  pagination: {
    current_page: number
    total_pages: number
    total_items: number
    page_size: number
    has_next: boolean
    has_previous: boolean
  }
}

// Country item returned by /api/companies/countries/
declare interface CountryItem {
  name: string
  flag: string
}
