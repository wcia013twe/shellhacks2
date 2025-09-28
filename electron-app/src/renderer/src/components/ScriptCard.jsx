import PropTypes from 'prop-types'

function ScriptCard({ meta, isExpanded, code, loading, onToggle, onCopy }) {
  return (
    <section className={`script-card${isExpanded ? ' script-card--open' : ''}`}>
      <header className="script-card__header">
        <div className="script-card__summary">
          <h2 className="script-card__title">{meta.title}</h2>
          <p className="script-card__description">{meta.description}</p>
        </div>
        <div className="script-card__actions">
          <button type="button" className="btn btn--primary" onClick={() => onCopy(meta.id)}>
            Copy script
          </button>
          <button type="button" className="btn" onClick={() => onToggle(meta.id)}>
            {isExpanded ? 'Hide code' : 'View code'}
          </button>
        </div>
      </header>
      {meta.steps?.length ? (
        <ol className="script-card__steps">
          {meta.steps.map((step, index) => (
            <li key={index}>{step}</li>
          ))}
        </ol>
      ) : null}
      {isExpanded ? (
        <div className="script-card__code">
          {loading ? (
            <div className="script-card__loading">Loading script...</div>
          ) : (
            <pre>
              <code>{code}</code>
            </pre>
          )}
        </div>
      ) : null}
    </section>
  )
}

ScriptCard.propTypes = {
  meta: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    steps: PropTypes.arrayOf(PropTypes.string)
  }).isRequired,
  isExpanded: PropTypes.bool,
  code: PropTypes.string,
  loading: PropTypes.bool,
  onToggle: PropTypes.func.isRequired,
  onCopy: PropTypes.func.isRequired
}

ScriptCard.defaultProps = {
  isExpanded: false,
  code: '',
  loading: false
}

export default ScriptCard
