// Google Maps' plain directions URL scheme needs no API key:
// https://developers.google.com/maps/documentation/urls/get-started#directions-action
export function buildGoogleMapsDirectionsUrl(stops) {
  const findStop = (type) => stops.find((stop) => stop.type === type)

  const origin = findStop('current')
  const destination = findStop('dropoff')
  const waypoint = findStop('pickup')

  if (!origin || !destination) return null

  const params = new URLSearchParams({
    api: '1',
    origin: `${origin.lat},${origin.lng}`,
    destination: `${destination.lat},${destination.lng}`,
    travelmode: 'driving',
  })

  if (waypoint) {
    params.set('waypoints', `${waypoint.lat},${waypoint.lng}`)
  }

  return `https://www.google.com/maps/dir/?${params.toString()}`
}
