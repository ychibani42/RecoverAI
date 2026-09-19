import { ChevronDown, ChevronRight, Search } from 'lucide-react'
import { Fragment, useEffect, useMemo, useState } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import { getPatients } from '../lib/api'

const PAGE_SIZE = 20

export default function PatientsTable() {
  const { t } = useTranslation()
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [severityFilter, setSeverityFilter] = useState('')
  const [treatmentFilter, setTreatmentFilter] = useState('')
  const [page, setPage] = useState(0)
  const [expandedId, setExpandedId] = useState(null)

  useEffect(() => {
    getPatients()
      .then(setPatients)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const severityOptions = useMemo(
    () => [...new Set(patients.map((p) => p.gravedad).filter(Boolean))].sort(),
    [patients],
  )
  const treatmentOptions = useMemo(
    () => [...new Set(patients.map((p) => p.tratamiento).filter(Boolean))].sort(),
    [patients],
  )

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return patients.filter((p) => {
      if (severityFilter && p.gravedad !== severityFilter) return false
      if (treatmentFilter && p.tratamiento !== treatmentFilter) return false
      if (!q) return true
      return [
        p.case_id,
        p.sexo,
        p.fractura_tipo,
        p.fractura_zona,
        p.gravedad,
        p.tratamiento,
        p.mecanismo_lesion,
        p.nivel_actividad,
        ...(p.comorbilidades || []),
      ]
        .filter(Boolean)
        .some((field) => String(field).toLowerCase().includes(q))
    })
  }, [patients, search, severityFilter, treatmentFilter])

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const currentPage = Math.min(page, pageCount - 1)
  const pageItems = filtered.slice(currentPage * PAGE_SIZE, currentPage * PAGE_SIZE + PAGE_SIZE)

  const handleSearch = (value) => {
    setSearch(value)
    setPage(0)
  }

  const handleFilterChange = (setter) => (value) => {
    setter(value)
    setPage(0)
  }

  const toggleExpanded = (id) => {
    setExpandedId((current) => (current === id ? null : id))
  }

  return (
    <>
      <div className="patients-toolbar">
        <div className="patients-search">
          <Search />
          <input
            type="text"
            placeholder={t('patients.searchPlaceholder')}
            value={search}
            onChange={(e) => handleSearch(e.target.value)}
          />
        </div>
        <div className="patients-filters">
          <select
            value={severityFilter}
            onChange={(e) => handleFilterChange(setSeverityFilter)(e.target.value)}
          >
            <option value="">{t('patients.filterAllSeverity')}</option>
            {severityOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <select
            value={treatmentFilter}
            onChange={(e) => handleFilterChange(setTreatmentFilter)(e.target.value)}
          >
            <option value="">{t('patients.filterAllTreatment')}</option>
            {treatmentOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
        <span className="patients-count">{t('patients.count', { count: filtered.length })}</span>
      </div>

      {loading && <p className="card-hint">{t('patients.loading')}</p>}
      {error && (
        <div className="error-box">
          <span>{t('patients.error', { message: error })}</span>
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="patients-table-wrap">
            <table className="patients-table">
              <thead>
                <tr>
                  <th aria-label={t('patients.columns.details')} />
                  <th>{t('patients.columns.caseId')}</th>
                  <th>{t('patients.columns.sex')}</th>
                  <th>{t('patients.columns.age')}</th>
                  <th>{t('patients.columns.imc')}</th>
                  <th>{t('patients.columns.activityLevel')}</th>
                  <th>{t('patients.columns.fracture')}</th>
                  <th>{t('patients.columns.zone')}</th>
                  <th>{t('patients.columns.severity')}</th>
                  <th>{t('patients.columns.mechanism')}</th>
                  <th>{t('patients.columns.treatment')}</th>
                  <th>{t('patients.columns.complications')}</th>
                  <th>{t('patients.columns.score')}</th>
                  <th>{t('patients.columns.recoveryWeeks')}</th>
                </tr>
              </thead>
              <tbody>
                {pageItems.map((p) => {
                  const id = p.uuid || p.case_id
                  const isExpanded = expandedId === id
                  return (
                    <Fragment key={id}>
                      <tr className={isExpanded ? 'expanded' : ''}>
                        <td>
                          <button
                            type="button"
                            className="patients-row-toggle"
                            onClick={() => toggleExpanded(id)}
                            aria-label={isExpanded ? t('patients.collapseRow') : t('patients.expandRow')}
                            title={isExpanded ? t('patients.collapseRow') : t('patients.expandRow')}
                          >
                            {isExpanded ? <ChevronDown /> : <ChevronRight />}
                          </button>
                        </td>
                        <td>{p.case_id}</td>
                        <td>{p.sexo}</td>
                        <td>{p.edad}</td>
                        <td>{p.imc}</td>
                        <td>{p.nivel_actividad}</td>
                        <td>{p.fractura_tipo}</td>
                        <td>{p.fractura_zona}</td>
                        <td>
                          <span className={`badge severity-${p.gravedad}`}>{p.gravedad}</span>
                        </td>
                        <td>{p.mecanismo_lesion}</td>
                        <td>{p.tratamiento}</td>
                        <td>{p.complicaciones}</td>
                        <td>{p.puntuacion_resultado}</td>
                        <td>{p.semanas_recuperacion_total}</td>
                      </tr>
                      {isExpanded && (
                        <tr className="patients-detail-row">
                          <td colSpan={14}>
                            <div className="patients-detail-grid">
                              <div className="patients-detail-section">
                                <h4>{t('patients.detail.anthropometry')}</h4>
                                <p>
                                  {t('patients.detail.height')}: {p.altura_cm} cm ·{' '}
                                  {t('patients.detail.weight')}: {p.peso_kg} kg
                                  <br />
                                  {t('patients.detail.athlete')}:{' '}
                                  {p.deportista ? t('patients.yes') : t('patients.no')}
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
                                <h4>{t('patients.detail.milestones')}</h4>
                                {p.hitos_recuperacion?.length ? (
                                  <ul>
                                    {p.hitos_recuperacion.map((hito) => (
                                      <li key={hito.semana}>
                                        {t('patients.detail.milestoneWeek', { week: hito.semana })}: {hito.hito}
                                      </li>
                                    ))}
                                  </ul>
                                ) : (
                                  <p>{t('patients.detail.none')}</p>
                                )}
                              </div>
                              <div className="patients-detail-section patients-detail-full">
                                <h4>{t('patients.detail.diagnosis')}</h4>
                                <p>{p.diagnostico_texto || t('patients.detail.none')}</p>
                              </div>
                              <div className="patients-detail-section patients-detail-full">
                                <h4>{t('patients.detail.imagingFindings')}</h4>
                                <p>{p.hallazgos_imagen_texto || t('patients.detail.none')}</p>
                              </div>
                              <div className="patients-detail-section patients-detail-full">
                                <h4>{t('patients.detail.recoveryPlan')}</h4>
                                <p>{p.plan_recuperacion_texto || t('patients.detail.none')}</p>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  )
                })}
                {pageItems.length === 0 && (
                  <tr>
                    <td colSpan={14} className="patients-empty">
                      {t('patients.noResults')}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="patients-pagination">
            <button type="button" disabled={currentPage === 0} onClick={() => setPage((p) => p - 1)}>
              {t('patients.prev')}
            </button>
            <span>{t('patients.pageInfo', { page: currentPage + 1, pages: pageCount })}</span>
            <button
              type="button"
              disabled={currentPage >= pageCount - 1}
              onClick={() => setPage((p) => p + 1)}
            >
              {t('patients.next')}
            </button>
          </div>
        </>
      )}
    </>
  )
}
