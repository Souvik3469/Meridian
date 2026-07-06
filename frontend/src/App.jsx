import { useState } from 'react'
import './App.css'
import { planTrip } from './api/tripService'
import LogSheetList from './components/LogSheetList'
import MapView from './components/MapView'
import StatTiles from './components/StatTiles'
import TripForm from './components/TripForm'

function App() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (payload) => {
    setIsSubmitting(true)
    setError(null)
    setResult(null)
    try {
      setResult(await planTrip(payload))
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>ELD Trip Planner</h1>
        <p className="app-subtitle">
          Plan a compliant route and auto-fill your FMCSA daily logs.
        </p>
      </header>

      <div className="card">
        <TripForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
      </div>

      {error && (
        <div className="alert alert--critical" role="alert">
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
            <div className="alert alert--warning" role="alert">
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
          <StatTiles route={result.route} dayCount={result.days.length} summary={result.summary} />
          <MapView route={result.route} />
          <LogSheetList days={result.days} />
        </div>
      )}
    </div>
  )
}

export default App
