import { useMemo, useState } from 'react'
import { Radar, User, X } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'

const SEVERITY_COLORS = {
  leve: '#16a34a',
  moderada: '#d97706',
  grave: '#dc2626',
}

const SIZE = 320
const CENTER = SIZE / 2
const MIN_RADIUS = 30
const MAX_RADIUS = 130

export default function NeighborsMap({ cases }) {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const [selectedId, setSelectedId] = useState(null)

  const points = useMemo(() => {
    if (!cases || cases.length === 0) return []
    return cases.map(({ case: p, similarity_score: score, final_score: finalScore }, index) => {
      const closeness = finalScore ?? score
      const distance = Math.min(Math.max(1 - closeness, 0), 1)
      const radius = MIN_RADIUS + distance * (MAX_RADIUS - MIN_RADIUS)
      const angle = (index / cases.length) * Math.PI * 2 - Math.PI / 2
      return {
        id: p.uuid || p.case_id,
        case: p,
        score: closeness,
        x: CENTER + radius * Math.cos(angle),
        y: CENTER + radius * Math.sin(angle),
        color: SEVERITY_COLORS[p.gravedad] || 'var(--brand)',
      }
    })
  }, [cases])

  if (!cases || cases.length === 0) return null

  const selected = points.find((pt) => pt.id === selectedId) || null

  return (
    <div className="report-section neighbors-map-section">
      <button type="button" className="ghost" onClick={() => setOpen((v) => !v)}>
        <Radar />
        {open ? t('report.neighborsMapHide') : t('report.neighborsMapButton')}
      </button>

      {open && (
        <div className="neighbors-map">
          <p className="card-hint">{t('report.neighborsMapHint')}</p>

          <svg
            viewBox={`0 0 ${SIZE} ${SIZE}`}
            className="neighbors-map-svg"
            role="img"
            aria-label={t('report.neighborsMapTitle')}
          >
            {[0.33, 0.66, 1].map((f) => (
              <circle
                key={f}
                cx={CENTER}
                cy={CENTER}
                r={MIN_RADIUS + f * (MAX_RADIUS - MIN_RADIUS)}
                className="neighbors-map-ring"
              />
            ))}

            {points.map((pt) => (
              <line key={`line-${pt.id}`} x1={CENTER} y1={CENTER} x2={pt.x} y2={pt.y} className="neighbors-map-line" />
            ))}

            {points.map((pt, index) => (
              <g
                key={pt.id}
                className={`neighbors-map-node ${selectedId === pt.id ? 'selected' : ''}`}
                onClick={() => setSelectedId((current) => (current === pt.id ? null : pt.id))}
              >
                <circle cx={pt.x} cy={pt.y} r={10} fill={pt.color} />
                <text x={pt.x} y={pt.y + 4} textAnchor="middle" className="neighbors-map-node-label">
                  {index + 1}
                </text>
                <title>
                  {pt.case.case_id} · {(pt.score * 100).toFixed(0)}%
                </title>
              </g>
            ))}

            <circle cx={CENTER} cy={CENTER} r={16} className="neighbors-map-center" />
            <g transform={`translate(${CENTER - 9}, ${CENTER - 9})`} className="neighbors-map-center-icon">
              <User width={18} height={18} />
              <title>{t('report.neighborsMapPatient')}</title>
            </g>
          </svg>

          <div className="neighbors-map-legend">
            {Object.entries(SEVERITY_COLORS).map(([level, color]) => (
              <span key={level}>
                <i className="legend-dot" style={{ background: color }} />
                {level}
              </span>
            ))}
          </div>

          {selected && (
            <div className="neighbors-map-detail">
              <button
                type="button"
                className="neighbors-map-detail-close"
                onClick={() => setSelectedId(null)}
                aria-label={t('report.neighborsMapClose')}
              >
                <X />
              </button>
              <strong>{selected.case.case_id}</strong>
              <span>
                {selected.case.sexo}, {selected.case.edad} {t('patients.columns.age').toLowerCase()} ·{' '}
                {selected.case.fractura_tipo}
              </span>
              <span>
                {t('report.similarityScore')}: {(selected.score * 100).toFixed(1)}%
              </span>
              <span>{selected.case.tratamiento}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
