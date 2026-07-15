import { useState } from 'react'
import './App.css'
import { planTrip } from './api/tripService'
import LogSheetList from './components/LogSheetList'
import MapView from './components/MapView'
import StatTiles from './components/StatTiles'
import TripForm from './components/TripForm'

function App() {
  const [result, setResult] = useState(null)
  const [tripInputs, setTripInputs] = useState(null)
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (payload) => {
    setIsSubmitting(true)
    setError(null)
    setResult(null)
    try {
      setResult(await planTrip(payload))
      setTripInputs(payload)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header no-print">
        <h1>Meridian</h1>
        <p className="app-subtitle">
          Plan a compliant route and auto-fill your FMCSA daily logs.
        </p>
      </header>

      <div className="card no-print">
        <TripForm onSubmit={handleSubmit} isSubmitting={isSubmitting} hasResult={Boolean(result)} />
      </div>

      {error && (
        <div className="alert alert--critical no-print" role="alert">
          <span className="alert__icon" aria-hidden="true">
            !
          </span>
          <span>
            <strong>Couldn&apos;t plan this trip.</strong> {error}
          </span>
        </div>
      )}

      {result && (
        <div className="results">
          {result.summary.requires_34_hour_restart && (
            <div className="alert alert--warning no-print" role="alert">
              <span className="alert__icon alert__icon--warning" aria-hidden="true">
                !
              </span>
              <span>
                <strong>34-hour restart required.</strong> Your available cycle hours run
                out partway through this trip, adding a mandatory 34-hour break before
                driving can resume.
              </span>
            </div>
          )}
          <div className="no-print">
            <StatTiles route={result.route} dayCount={result.days.length} summary={result.summary} />
          </div>
          <div className="no-print">
            <MapView route={result.route} />
          </div>

          <div className="results-actions no-print">
            <span className="print-hint">Choose &quot;Landscape&quot; in the print dialog for best results</span>
            <button type="button" className="print-button" onClick={() => window.print()}>
              Print / Save as PDF
            </button>
          </div>
          <LogSheetList days={result.days} tripInputs={tripInputs} />
        </div>
      )}
    </div>
  )
}

export default App
