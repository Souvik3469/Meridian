import { useState } from 'react'
import LocationAutocomplete from './LocationAutocomplete'

const INITIAL_VALUES = {
  current_location: '',
  current_cycle_used_hours: '',
  trip_start_time: '',
}

const INITIAL_STOPS = [
  { location: '', type: 'pickup', extra_delay_hours: '' },
  { location: '', type: 'dropoff', extra_delay_hours: '' },
]

const MIN_STOPS = 2

function TripForm({ onSubmit, isSubmitting, hasResult }) {
  const [values, setValues] = useState(INITIAL_VALUES)
  const [stops, setStops] = useState(INITIAL_STOPS)

  const setField = (name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }))
  }

  const handleChange = (event) => {
    setField(event.target.name, event.target.value)
  }

  const setStopField = (index, field, value) => {
    setStops((prev) => prev.map((stop, i) => (i === index ? { ...stop, [field]: value } : stop)))
  }

  const addStop = () => {
    setStops((prev) => [...prev, { location: '', type: 'dropoff', extra_delay_hours: '' }])
  }

  const removeStop = (index) => {
    setStops((prev) => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    onSubmit({
      ...values,
      stops: stops.map((stop) => ({
        ...stop,
        extra_delay_hours: Number(stop.extra_delay_hours) || 0,
      })),
      current_cycle_used_hours: Number(values.current_cycle_used_hours),
      trip_start_time: values.trip_start_time || null,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="trip-form">
      <LocationAutocomplete
        name="current_location"
        label="Current location"
        value={values.current_location}
        onChange={setField}
        placeholder="Denver, CO"
        required
      />

      <div className="trip-form__stops">
        {stops.map((stop, index) => (
          <div key={index} className="trip-form__stop-row">
            <LocationAutocomplete
              name={`stop-location-${index}`}
              label={`Stop ${index + 1} location`}
              value={stop.location}
              onChange={(_, value) => setStopField(index, 'location', value)}
              placeholder={index === 0 ? 'Colorado Springs, CO' : 'Albuquerque, NM'}
              required
            />
            <label>
              Type
              <select value={stop.type} onChange={(event) => setStopField(index, 'type', event.target.value)}>
                <option value="pickup">Pickup</option>
                <option value="dropoff">Dropoff</option>
              </select>
            </label>
            <label>
              Delay <span className="label-hint">(hrs)</span>
              <input
                type="number"
                min="0"
                max="24"
                step="0.5"
                placeholder="0"
                value={stop.extra_delay_hours}
                onChange={(event) => setStopField(index, 'extra_delay_hours', event.target.value)}
              />
            </label>
            {stops.length > MIN_STOPS && (
              <button
                type="button"
                className="trip-form__remove-stop"
                onClick={() => removeStop(index)}
                aria-label={`Remove stop ${index + 1}`}
              >
                &times;
              </button>
            )}
          </div>
        ))}
        <button type="button" className="trip-form__add-stop" onClick={addStop}>
          + Add stop
        </button>
      </div>

      <label>
        Current cycle used (hrs)
        <input
          name="current_cycle_used_hours"
          type="number"
          min="0"
          max="70"
          step="0.5"
          value={values.current_cycle_used_hours}
          onChange={handleChange}
          placeholder="0"
          required
        />
      </label>
      <label>
        Trip start time <span className="label-hint">(optional, defaults to midnight)</span>
        <input
          name="trip_start_time"
          type="time"
          value={values.trip_start_time}
          onChange={handleChange}
        />
      </label>
      <button type="submit" className="trip-form__submit" disabled={isSubmitting}>
        {isSubmitting ? 'Planning…' : hasResult ? 'Replan trip' : 'Plan trip'}
      </button>
    </form>
  )
}

export default TripForm
