const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export async function planTrip(payload) {
  const response = await fetch(`${API_BASE_URL}/api/trips/plan/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  const data = await response.json()

  if (!response.ok) {
    const message = data.detail || Object.values(data).flat().join(' ')
    throw new Error(message || 'Failed to plan trip')
  }

  return data
}
