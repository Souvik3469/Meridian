import { useState } from 'react'
import './App.css'
import { planTrip } from './api/tripService'
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
      <h1>ELD Trip Planner</h1>
      <TripForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="result-summary">
          <p>
            {result.route.distance_miles.toFixed(1)} miles &middot;{' '}
            {result.route.duration_hours.toFixed(1)} hrs driving
          </p>
          <p>
            {result.days.length} day{result.days.length > 1 ? 's' : ''} of duty logs generated
          </p>
        </div>
      )}
    </div>
  )
}

export default App
