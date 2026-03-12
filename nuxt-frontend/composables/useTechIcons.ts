/**
 * useTechIcons — resolves technology names to icon URLs served from Django static.
 * No list pre-fetch: the URL is constructed directly from the tech name.
 * Use @error on <img> tags to handle missing icons gracefully.
 */
export function useTechIcons() {
  const config = useRuntimeConfig()
  const staticBase = config.public.staticBase as string

  /** Returns the expected SVG URL for a tech name. Use @error on <img> to hide if missing. */
  function iconUrl(techName: string): string {
    const slug = techName.toLowerCase().trim()
      .replace(/[\s.]+/g, '-')
      .replace(/[^a-z0-9-]/g, '')
    return `${staticBase}/icons/${slug}.svg`
  }

  function splitTechs(technologies: string): string[] {
    return technologies.split(',').map(t => t.trim()).filter(Boolean)
  }

  return { iconUrl, splitTechs }
}

