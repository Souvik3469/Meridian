import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
import { MapContainer, Marker, Polyline, Popup, TileLayer } from 'react-leaflet'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
})

function MapView({ route }) {
  if (!route || route.geometry.length === 0) return null

  const center = route.geometry[Math.floor(route.geometry.length / 2)]

  return (
    <MapContainer center={center} zoom={6} scrollWheelZoom={false} className="map-view">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Polyline positions={route.geometry} color="#2563eb" weight={4} />
      {route.stops.map((stop, index) => (
        <Marker key={`${stop.type}-${index}`} position={[stop.lat, stop.lng]}>
          <Popup>
            <strong>{stop.type}</strong>
            <br />
            {stop.label}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}

export default MapView
