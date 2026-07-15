const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export async function getLocationSuggestions(query, signal) {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/autocomplete/?q=${encodeURIComponent(query)}`,
    { signal }
  )

  if (!response.ok) return []

  const data = await response.json()
  return data.results || []
}
