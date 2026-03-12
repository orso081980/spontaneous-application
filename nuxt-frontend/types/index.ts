// Shared TypeScript interfaces matching the Django REST API serializers

export interface Company {
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

export interface UserProfile {
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

export interface JobApplication {
  id: string
  company: string
  company_name: string
  user_profile: string
  position: string
  project_to_suggest: string
  link_to_project: string
  message: string
  status: 'created' | 'sent' | 'interview' | 'accepted' | 'refused'
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
