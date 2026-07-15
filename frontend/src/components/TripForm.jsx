import { useState } from 'react'
import LocationAutocomplete from './LocationAutocomplete'

const INITIAL_VALUES = {
  current_location: '',
  pickup_location: '',
  dropoff_location: '',
  current_cycle_used_hours: '',
  trip_start_time: '',
}

function TripForm({ onSubmit, isSubmitting }) {
  const [values, setValues] = useState(INITIAL_VALUES)

  const setField = (name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }))
  }

  const handleChange = (event) => {
    setField(event.target.name, event.target.value)
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    onSubmit({
      ...values,
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
      <LocationAutocomplete
        name="pickup_location"
        label="Pickup location"
        value={values.pickup_location}
        onChange={setField}
        placeholder="Colorado Springs, CO"
        required
      />
      <LocationAutocomplete
        name="dropoff_location"
        label="Dropoff location"
        value={values.dropoff_location}
        onChange={setField}
        placeholder="Albuquerque, NM"
        required
      />
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
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Planning…' : 'Plan trip'}
      </button>
    </form>
  )
}

export default TripForm
