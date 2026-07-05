import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { MapContainer, Marker, Polyline, Popup, TileLayer } from 'react-leaflet'

const STOP_LABELS = {
  current: 'Current location',
  pickup: 'Pickup',
  dropoff: 'Dropoff',
  rest: 'Rest stop',
  fuel: 'Fuel stop',
}

function createStopIcon(type) {
  return L.divIcon({
    className: 'stop-marker',
    html: `<span class="dot dot--${type}"></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  })
}

function MapView({ route }) {
  if (!route || route.geometry.length === 0) return null

  const center = route.geometry[Math.floor(route.geometry.length / 2)]

  return (
    <div className="map-card">
      <MapContainer center={center} zoom={6} scrollWheelZoom={false} className="map-view">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Polyline positions={route.geometry} pathOptions={{ className: 'route-line' }} weight={4} />
        {route.stops.map((stop, index) => (
          <Marker key={`${stop.type}-${index}`} position={[stop.lat, stop.lng]} icon={createStopIcon(stop.type)}>
            <Popup>
              <strong>{STOP_LABELS[stop.type] || stop.type}</strong>
              <br />
              {stop.label}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      <ul className="legend">
        {Object.entries(STOP_LABELS).map(([type, label]) => (
          <li key={type} className="legend__item">
            <span className={`dot dot--${type}`} />
            {label}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default MapView
