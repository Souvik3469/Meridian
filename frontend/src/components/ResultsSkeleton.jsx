function ResultsSkeleton() {
  return (
    <div className="skeleton no-print" aria-hidden="true">
      <div className="skeleton__tiles">
        {Array.from({ length: 4 }, (_, i) => (
          <div key={i} className="skeleton__block skeleton__tile" />
        ))}
      </div>
      <div className="skeleton__block skeleton__map" />
      <div className="skeleton__block skeleton__sheet" />
    </div>
  )
}

export default ResultsSkeleton
