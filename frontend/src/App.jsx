import { useState } from 'react'
import './App.css'
import { planTrip } from './api/tripService'
import AppHeader from './components/AppHeader'
import HowItWorks from './components/HowItWorks'
import LogSheetList from './components/LogSheetList'
import MapView from './components/MapView'
import ResultsSkeleton from './components/ResultsSkeleton'
import StatTiles from './components/StatTiles'
import TripForm from './components/TripForm'
import { useTheme } from './hooks/useTheme'

function App() {
  const { theme, toggleTheme } = useTheme()
  const [result, setResult] = useState(null)
  const [tripInputs, setTripInputs] = useState(null)
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [hasPlannedOnce, setHasPlannedOnce] = useState(false)

  const handleSubmit = async (payload) => {
    setIsSubmitting(true)
    setError(null)
    setResult(null)
    try {
      setResult(await planTrip(payload))
      setTripInputs(payload)
      setHasPlannedOnce(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="app">
      <AppHeader theme={theme} onToggleTheme={toggleTheme} />

      <main className="app-main">
        {hasPlannedOnce ? (
          <div className="card trip-form-card no-print">
            <h2 className="card__title">Trip details</h2>
            <TripForm onSubmit={handleSubmit} isSubmitting={isSubmitting} hasResult={Boolean(result)} />
          </div>
        ) : (
          <div className="layout-intro">
            <HowItWorks />
            <div className="card trip-form-card no-print">
              <h2 className="card__title">Plan your trip</h2>
              <TripForm onSubmit={handleSubmit} isSubmitting={isSubmitting} hasResult={Boolean(result)} />
            </div>
          </div>
        )}

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

        {isSubmitting && <ResultsSkeleton />}

        {result && !isSubmitting && (
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
      </main>

      <footer className="app-footer no-print">
        <p>Meridian is a pre-trip planning tool. It doesn&apos;t replace a certified ELD.</p>
      </footer>
    </div>
  )
}

export default App
