import { useEffect, useRef, useState } from 'react'
import { getLocationSuggestions } from '../api/locationService'

const DEBOUNCE_MS = 300
const MIN_QUERY_LENGTH = 3

function LocationAutocomplete({ name, label, value, onChange, placeholder, required }) {
  const [suggestions, setSuggestions] = useState([])
  const [isOpen, setIsOpen] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const skipNextLookupRef = useRef(false)
  const isFocusedRef = useRef(false)
  const requestIdRef = useRef(0)

  useEffect(() => {
    if (skipNextLookupRef.current) {
      skipNextLookupRef.current = false
      return
    }

    if (value.trim().length < MIN_QUERY_LENGTH) {
      setSuggestions([])
      setIsOpen(false)
      setIsSearching(false)
      return
    }

    // Guards against a slower, now-stale request resolving after a newer
    // one — without this, a fast second keystroke's spinner could get
    // turned off by the first keystroke's request finishing later.
    const requestId = ++requestIdRef.current
    setIsSearching(true)

    const controller = new AbortController()
    const timer = setTimeout(async () => {
      try {
        const results = await getLocationSuggestions(value, controller.signal)
        if (requestIdRef.current !== requestId) return
        setSuggestions(results)
        // The field may have lost focus while this was in flight — don't
        // force a dropdown open on a field the user has already left.
        setIsOpen(isFocusedRef.current && results.length > 0)
        setActiveIndex(-1)
        setIsSearching(false)
      } catch {
        // Aborted or network hiccup — suggestions are a soft affordance, fail silently.
        if (requestIdRef.current === requestId) setIsSearching(false)
      }
    }, DEBOUNCE_MS)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [value])

  const handleSelect = (suggestion) => {
    skipNextLookupRef.current = true
    onChange(name, suggestion.label)
    setSuggestions([])
    setIsOpen(false)
  }

  const handleKeyDown = (event) => {
    if (!isOpen || suggestions.length === 0) return

    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setActiveIndex((prev) => (prev + 1) % suggestions.length)
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((prev) => (prev - 1 + suggestions.length) % suggestions.length)
    } else if (event.key === 'Enter' && activeIndex >= 0) {
      event.preventDefault()
      handleSelect(suggestions[activeIndex])
    } else if (event.key === 'Escape') {
      setIsOpen(false)
    }
  }

  return (
    <label className="location-autocomplete">
      {label}
      <div className="location-autocomplete__input-wrap">
        <input
          name={name}
          value={value}
          onChange={(event) => onChange(name, event.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            isFocusedRef.current = true
          }}
          onBlur={() => {
            isFocusedRef.current = false
            setTimeout(() => {
              setIsOpen(false)
              setSuggestions([])
              setIsSearching(false)
            }, 150)
          }}
          placeholder={placeholder}
          required={required}
          autoComplete="off"
          role="combobox"
          aria-expanded={isOpen}
          aria-autocomplete="list"
          aria-busy={isSearching}
        />
        {isSearching && (
          <span className="location-autocomplete__spinner" aria-hidden="true" />
        )}
        {isOpen && (
          <ul className="location-autocomplete__suggestions" role="listbox">
            {suggestions.map((suggestion, index) => (
              <li
                key={`${suggestion.label}-${index}`}
                role="option"
                aria-selected={index === activeIndex}
                className={index === activeIndex ? 'is-active' : ''}
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => handleSelect(suggestion)}
              >
                {suggestion.label}
              </li>
            ))}
          </ul>
        )}
      </div>
    </label>
  )
}

export default LocationAutocomplete
