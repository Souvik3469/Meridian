const STEPS = [
  {
    title: 'Enter your trip',
    description: 'Current location, pickup and dropoff stops, and hours already used in your cycle.',
  },
  {
    title: 'We run the HOS math',
    description: '11-hour driving, 14-hour window, 30-minute breaks, 70-hour/8-day limits — all checked automatically.',
  },
  {
    title: 'Get your route + logs',
    description: 'A mapped route with every rest and fuel stop, plus a pre-drawn FMCSA log sheet for each day.',
  },
]

function HowItWorks() {
  return (
    <div className="how-it-works no-print">
      <h2 className="how-it-works__title">How it works</h2>
      <ol className="how-it-works__steps">
        {STEPS.map((step, index) => (
          <li key={step.title} className="how-it-works__step">
            <span className="how-it-works__number">{index + 1}</span>
            <div>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}

export default HowItWorks
