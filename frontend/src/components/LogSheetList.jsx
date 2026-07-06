import LogSheet from './LogSheet'

function LogSheetList({ days, tripInputs }) {
  return (
    <div className="log-sheet-list">
      {tripInputs && (
        <p className="print-only log-sheet-list__trip-context">
          {tripInputs.current_location} &rarr; {tripInputs.pickup_location} &rarr;{' '}
          {tripInputs.dropoff_location}
        </p>
      )}
      {days.map((day) => (
        <LogSheet key={day.day_number} day={day} />
      ))}
    </div>
  )
}

export default LogSheetList
