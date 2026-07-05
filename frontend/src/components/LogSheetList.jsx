import LogSheet from './LogSheet'

function LogSheetList({ days }) {
  return (
    <div className="log-sheet-list">
      {days.map((day) => (
        <LogSheet key={day.day_number} day={day} />
      ))}
    </div>
  )
}

export default LogSheetList
