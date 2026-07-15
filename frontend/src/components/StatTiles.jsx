function formatTripDuration(hours) {
  if (hours < 24) return `${hours.toFixed(1)} hrs`
  const days = Math.floor(hours / 24)
  const remainingHours = hours - days * 24
  return `${days}d ${remainingHours.toFixed(1)}h`
}

const ICONS = {
  distance: (
    <path d="M4 20 L10 6 L14 15 L17 8 L20 20" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 7v5.5l4 2.3" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </>
  ),
  calendar: (
    <>
      <rect x="4" y="5.5" width="16" height="14.5" rx="2" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path d="M4 10h16M8 3.5v3.5M16 3.5v3.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </>
  ),
  sheets: (
    <>
      <rect x="5" y="3.5" width="14" height="17" rx="1.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path d="M8 8h8M8 12h8M8 16h5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </>
  ),
}

function StatIcon({ name }) {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" className="stat-tile__icon">
      {ICONS[name]}
    </svg>
  )
}

function StatTiles({ route, dayCount, summary }) {
  return (
    <div className="stat-tiles">
      <div className="stat-tile">
        <StatIcon name="distance" />
        <span className="stat-tile__label">Distance</span>
        <span className="stat-tile__value">{route.distance_miles.toFixed(0)} mi</span>
      </div>
      <div className="stat-tile">
        <StatIcon name="clock" />
        <span className="stat-tile__label">Driving time</span>
        <span className="stat-tile__value">{route.duration_hours.toFixed(1)} hrs</span>
      </div>
      <div className="stat-tile">
        <StatIcon name="calendar" />
        <span className="stat-tile__label">Total trip time</span>
        <span className="stat-tile__value">{formatTripDuration(summary.total_trip_hours)}</span>
      </div>
      <div className="stat-tile">
        <StatIcon name="sheets" />
        <span className="stat-tile__label">Log sheets</span>
        <span className="stat-tile__value">
          {dayCount} day{dayCount > 1 ? 's' : ''}
        </span>
      </div>
    </div>
  )
}

export default StatTiles
