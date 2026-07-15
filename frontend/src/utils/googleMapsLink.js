// Google Maps' plain directions URL scheme needs no API key:
// https://developers.google.com/maps/documentation/urls/get-started#directions-action
export function buildGoogleMapsDirectionsUrl(stops) {
  // Only the trip's real (non-interpolated) stops — current location plus
  // every pickup/dropoff the driver entered, in order. Rest/fuel stops are
  // computed points along the route, not places to route through.
  const realStops = stops.filter((stop) => stop.type === 'current' || stop.type === 'pickup' || stop.type === 'dropoff')

  if (realStops.length < 2) return null

  const origin = realStops[0]
  const destination = realStops[realStops.length - 1]
  const waypoints = realStops.slice(1, -1)

  const params = new URLSearchParams({
    api: '1',
    origin: `${origin.lat},${origin.lng}`,
    destination: `${destination.lat},${destination.lng}`,
    travelmode: 'driving',
  })

  if (waypoints.length > 0) {
    params.set('waypoints', waypoints.map((stop) => `${stop.lat},${stop.lng}`).join('|'))
  }

  return `https://www.google.com/maps/dir/?${params.toString()}`
}
