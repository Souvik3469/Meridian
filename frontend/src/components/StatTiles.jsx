function formatTripDuration(hours) {
  if (hours < 24) return `${hours.toFixed(1)} hrs`
  const days = Math.floor(hours / 24)
  const remainingHours = hours - days * 24
  return `${days}d ${remainingHours.toFixed(1)}h`
}

function StatTiles({ route, dayCount, summary }) {
  return (
    <div className="stat-tiles">
      <div className="stat-tile">
        <span className="stat-tile__label">Distance</span>
        <span className="stat-tile__value">{route.distance_miles.toFixed(0)} mi</span>
      </div>
      <div className="stat-tile">
        <span className="stat-tile__label">Driving time</span>
        <span className="stat-tile__value">{route.duration_hours.toFixed(1)} hrs</span>
      </div>
      <div className="stat-tile">
        <span className="stat-tile__label">Total trip time</span>
        <span className="stat-tile__value">{formatTripDuration(summary.total_trip_hours)}</span>
      </div>
      <div className="stat-tile">
        <span className="stat-tile__label">Log sheets</span>
        <span className="stat-tile__value">
          {dayCount} day{dayCount > 1 ? 's' : ''}
        </span>
      </div>
    </div>
  )
}

export default StatTiles
