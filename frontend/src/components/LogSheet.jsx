const ROWS = [
  { key: 'off_duty', label: '1. Off Duty' },
  { key: 'sleeper_berth', label: '2. Sleeper Berth' },
  { key: 'driving', label: '3. Driving' },
  { key: 'on_duty_not_driving', label: '4. On Duty (not driving)' },
]

const DUTY_COLOR_VARS = {
  off_duty: 'var(--duty-off-duty)',
  sleeper_berth: 'var(--duty-sleeper)',
  driving: 'var(--duty-driving)',
  on_duty_not_driving: 'var(--duty-on-duty)',
}

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

function rowIndex(status) {
  return ROWS.findIndex((row) => row.key === status)
}

function rowY(status) {
  return HEADER_HEIGHT + rowIndex(status) * ROW_HEIGHT + ROW_HEIGHT / 2
}

function formatHourLabel(hour) {
  if (hour === 0 || hour === 24) return 'Midnight'
  if (hour === 12) return 'Noon'
  return hour > 12 ? `${hour - 12}` : `${hour}`
}

function DutyStepLine({ entries }) {
  return (
    <>
      {entries.map((entry, index) => {
        const y = rowY(entry.status)
        const x1 = hourToX(entry.start_hour)
        const x2 = hourToX(entry.end_hour)
        const previous = entries[index - 1]

        return (
          <g key={index}>
            {previous && (
              <line x1={x1} y1={rowY(previous.status)} x2={x1} y2={y} style={{ stroke: 'var(--ink-muted)' }} strokeWidth={2} />
            )}
            <line
              x1={x1}
              y1={y}
              x2={x2}
              y2={y}
              style={{ stroke: DUTY_COLOR_VARS[entry.status] }}
              strokeWidth={2}
              strokeLinecap="round"
            />
          </g>
        )
      })}
    </>
  )
}

function LogSheet({ day }) {
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
              style={{ fill: index % 2 === 0 ? 'var(--surface)' : 'var(--page)' }}
            />
            <circle
              cx={12}
              cy={HEADER_HEIGHT + index * ROW_HEIGHT + ROW_HEIGHT / 2}
              r={4}
              style={{ fill: DUTY_COLOR_VARS[row.key] }}
            />
            <text
              x={24}
              y={HEADER_HEIGHT + index * ROW_HEIGHT + ROW_HEIGHT / 2 + 4}
              fontSize="11"
              style={{ fill: 'var(--ink-secondary)' }}
            >
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
            style={{ stroke: hour % 6 === 0 ? 'var(--border)' : 'var(--gridline)' }}
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
            style={{ fill: 'var(--ink-muted)' }}
          >
            {formatHourLabel(hour)}
          </text>
        ))}

        <line
          x1={LABEL_WIDTH}
          y1={HEADER_HEIGHT}
          x2={LABEL_WIDTH}
          y2={TOTAL_HEIGHT}
          style={{ stroke: 'var(--border)' }}
        />
        <DutyStepLine entries={day.entries} />
      </svg>

      <ul className="log-sheet-totals">
        {ROWS.map((row) => (
          <li key={row.key} className="legend__item">
            <span className="dot" style={{ background: DUTY_COLOR_VARS[row.key] }} />
            {row.label}: {(day.totals[row.key] || 0).toFixed(1)} hrs
          </li>
        ))}
      </ul>
    </div>
  )
}

export default LogSheet
