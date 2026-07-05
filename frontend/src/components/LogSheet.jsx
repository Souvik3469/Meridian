const ROWS = [
  { key: 'off_duty', label: '1. Off Duty' },
  { key: 'sleeper_berth', label: '2. Sleeper Berth' },
  { key: 'driving', label: '3. Driving' },
  { key: 'on_duty_not_driving', label: '4. On Duty (not driving)' },
]

const HOUR_WIDTH = 30
const ROW_HEIGHT = 36
const LABEL_WIDTH = 170
const HEADER_HEIGHT = 24
const CHART_WIDTH = HOUR_WIDTH * 24
const CHART_HEIGHT = ROW_HEIGHT * ROWS.length
const TOTAL_WIDTH = LABEL_WIDTH + CHART_WIDTH
const TOTAL_HEIGHT = HEADER_HEIGHT + CHART_HEIGHT

function hourToX(hour) {
  return LABEL_WIDTH + hour * HOUR_WIDTH
}

function rowY(status) {
  const index = ROWS.findIndex((row) => row.key === status)
  return HEADER_HEIGHT + index * ROW_HEIGHT + ROW_HEIGHT / 2
}

function formatHourLabel(hour) {
  if (hour === 0 || hour === 24) return 'Midnight'
  if (hour === 12) return 'Noon'
  return hour > 12 ? `${hour - 12}` : `${hour}`
}

function buildStepPath(entries) {
  if (entries.length === 0) return ''

  let path = `M ${hourToX(entries[0].start_hour)} ${rowY(entries[0].status)}`
  entries.forEach((entry, index) => {
    if (index > 0) {
      path += ` L ${hourToX(entry.start_hour)} ${rowY(entry.status)}`
    }
    path += ` L ${hourToX(entry.end_hour)} ${rowY(entry.status)}`
  })
  return path
}

function LogSheet({ day }) {
  const path = buildStepPath(day.entries)

  return (
    <div className="log-sheet">
      <h3>Day {day.day_number}</h3>
      <svg viewBox={`0 0 ${TOTAL_WIDTH} ${TOTAL_HEIGHT}`} className="log-sheet-grid">
        {ROWS.map((row, index) => (
          <g key={row.key}>
            <rect
              x={0}
              y={HEADER_HEIGHT + index * ROW_HEIGHT}
              width={TOTAL_WIDTH}
              height={ROW_HEIGHT}
              fill={index % 2 === 0 ? '#fafafa' : '#ffffff'}
            />
            <text x={8} y={HEADER_HEIGHT + index * ROW_HEIGHT + ROW_HEIGHT / 2 + 4} fontSize="11">
              {row.label}
            </text>
          </g>
        ))}

        {Array.from({ length: 25 }, (_, hour) => (
          <line
            key={hour}
            x1={hourToX(hour)}
            y1={HEADER_HEIGHT}
            x2={hourToX(hour)}
            y2={TOTAL_HEIGHT}
            stroke="#ccc"
            strokeWidth={hour % 6 === 0 ? 1.2 : 0.5}
          />
        ))}

        {Array.from({ length: 24 }, (_, hour) => (
          <text
            key={hour}
            x={hourToX(hour) + HOUR_WIDTH / 2}
            y={HEADER_HEIGHT - 8}
            fontSize="9"
            textAnchor="middle"
          >
            {formatHourLabel(hour)}
          </text>
        ))}

        <line x1={LABEL_WIDTH} y1={HEADER_HEIGHT} x2={LABEL_WIDTH} y2={TOTAL_HEIGHT} stroke="#333" />
        <path d={path} fill="none" stroke="#1d4ed8" strokeWidth={2} />
      </svg>

      <ul className="log-sheet-totals">
        {ROWS.map((row) => (
          <li key={row.key}>
            {row.label}: {(day.totals[row.key] || 0).toFixed(1)} hrs
          </li>
        ))}
      </ul>
    </div>
  )
}

export default LogSheet
