import { ChevronDown, ChevronRight } from 'lucide-react'
import { Fragment, useState } from 'react'
import { useTranslation } from '../i18n/I18nContext'

export default function SimilarCasesList({ cases }) {
  const { t } = useTranslation()
  const [expandedId, setExpandedId] = useState(null)

  if (!cases || cases.length === 0) return null

  const toggleExpanded = (id) => {
    setExpandedId((current) => (current === id ? null : id))
  }

  return (
    <div className="report-section similar-cases">
      <div className="report-section-header">
        <h3>{t('report.similarCasesTitle')}</h3>
      </div>
      <p className="card-hint">{t('report.similarCasesHint', { count: cases.length })}</p>

      <ul className="similar-cases-list">
        {cases.map(({ case: p, similarity_score: score }, index) => {
          const id = p.uuid || p.case_id
          const isExpanded = expandedId === id
          return (
            <Fragment key={id}>
              <li className={`similar-case-item ${isExpanded ? 'expanded' : ''}`}>
                <button
                  type="button"
                  className="similar-case-toggle"
                  onClick={() => toggleExpanded(id)}
                  aria-expanded={isExpanded}
                >
                  <span className="similar-case-rank">#{index + 1}</span>
                  <span className="similar-case-summary">
                    <strong>{p.case_id}</strong> · {p.sexo}, {p.edad} {t('patients.columns.age').toLowerCase()} ·{' '}
                    {p.fractura_tipo} ({p.fractura_zona}) · {p.tratamiento}
                  </span>
                  <span className="badge similar-case-score">
                    {t('report.similarityScore')}: {(score * 100).toFixed(1)}%
                  </span>
                  {isExpanded ? <ChevronDown /> : <ChevronRight />}
                </button>

                {isExpanded && (
                  <div className="patients-detail-grid">
                    <div className="patients-detail-section">
                      <h4>{t('patients.detail.anthropometry')}</h4>
                      <p>
                        {t('patients.detail.height')}: {p.altura_cm} cm · {t('patients.detail.weight')}: {p.peso_kg} kg
                        · {t('patients.columns.imc')}: {p.imc}
                        <br />
                        {t('patients.detail.athlete')}: {p.deportista ? t('patients.yes') : t('patients.no')} ·{' '}
                        {t('patients.columns.activityLevel')}: {p.nivel_actividad}
                      </p>
                    </div>
                    <div className="patients-detail-section">
                      <h4>{t('patients.detail.comorbidities')}</h4>
                      {p.comorbilidades?.length ? (
                        <ul>
                          {p.comorbilidades.map((c) => (
                            <li key={c}>{c}</li>
                          ))}
                        </ul>
                      ) : (
                        <p>{t('patients.detail.none')}</p>
                      )}
                    </div>
                    <div className="patients-detail-section">
                      <h4>{t('patients.detail.treatmentDetail')}</h4>
                      <p>{p.tratamiento_detalle || t('patients.detail.none')}</p>
                      <p>
                        {t('patients.detail.recoveryBreakdown', {
                          stabilization: p.semanas_estabilizacion,
                          physio: p.semanas_fisioterapia,
                        })}
                      </p>
                    </div>
                    <div className="patients-detail-section">
                      <h4>{t('patients.columns.severity')}</h4>
                      <p>
                        <span className={`badge severity-${p.gravedad}`}>{p.gravedad}</span>
                      </p>
                      <p>
                        {t('patients.columns.complications')}: {p.complicaciones || t('patients.detail.none')}
                      </p>
                    </div>
                    <div className="patients-detail-section patients-detail-full">
                      <h4>{t('patients.detail.diagnosis')}</h4>
                      <p>{p.diagnostico_texto || t('patients.detail.none')}</p>
                    </div>
                    <div className="patients-detail-section patients-detail-full">
                      <h4>{t('patients.detail.recoveryPlan')}</h4>
                      <p>{p.plan_recuperacion_texto || t('patients.detail.none')}</p>
                    </div>
                  </div>
                )}
              </li>
            </Fragment>
          )
        })}
      </ul>
    </div>
  )
}
