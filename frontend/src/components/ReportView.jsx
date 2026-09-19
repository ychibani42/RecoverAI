import { Activity, AlertTriangle, ClipboardList, Clock, HeartPulse, Salad, Search, Stethoscope } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'

function Section({ icon: Icon, title, value }) {
  if (!value) return null
  return (
    <div className="report-section">
      <div className="report-section-header">
        <span className="section-icon">
          <Icon />
        </span>
        <h3>{title}</h3>
      </div>
      <p>{value}</p>
    </div>
  )
}

export default function ReportView({ report, loading }) {
  const { t } = useTranslation()

  if (loading) {
    return (
      <div className="report-empty loading">
        <span className="empty-icon">
          <Activity />
        </span>
        {t('report.loading')}
      </div>
    )
  }

  if (!report) {
    return (
      <div className="report-empty">
        <span className="empty-icon">
          <ClipboardList />
        </span>
        {t('report.empty')}
      </div>
    )
  }

  return (
    <div>
      <Section icon={Search} title={t('report.summary')} value={report.resumen_casos_similares} />
      <Section icon={Stethoscope} title={t('report.treatment')} value={report.tratamiento_recomendado} />

      <div className="report-section">
        <div className="report-section-header">
          <span className="section-icon">
            <Clock />
          </span>
          <h3>{t('report.recoveryTime')}</h3>
        </div>
        <span className="badge">
          <Clock />
          {report.tiempo_recuperacion_estimado}
        </span>
      </div>

      <Section icon={Salad} title={t('report.diet')} value={report.dieta_recomendada} />
      <Section icon={HeartPulse} title={t('report.habits')} value={report.habitos_salud_recomendados} />

      <div className="report-section">
        <div className="warning-box">
          <AlertTriangle />
          <span>{report.advertencia}</span>
        </div>
      </div>
    </div>
  )
}
