import { useEffect, useState } from 'react'
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  ClipboardList,
  Clock,
  HeartPulse,
  MessageSquare,
  Salad,
  Search,
  Stethoscope,
} from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'
import { sendAppointmentSms } from '../lib/api'
import SimilarCasesList from './SimilarCasesList'

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

function SmsAppointmentForm({ report }) {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const [phone, setPhone] = useState('')
  const [weeks, setWeeks] = useState(report.semanas_hasta_revision ?? 6)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  useEffect(() => {
    setOpen(false)
    setPhone('')
    setWeeks(report.semanas_hasta_revision ?? 6)
    setSending(false)
    setError('')
    setResult(null)
  }, [report])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!phone.trim()) {
      setError(t('report.smsValidationPhone'))
      return
    }
    setSending(true)
    setError('')
    try {
      const res = await sendAppointmentSms({ phone: phone.trim(), weeks: Number(weeks) })
      setResult(res)
    } catch (err) {
      setError(t('report.smsError', { message: err.message }))
    } finally {
      setSending(false)
    }
  }

  if (!open) {
    return (
      <div className="report-section sms-section">
        <button type="button" className="ghost" onClick={() => setOpen(true)}>
          <MessageSquare />
          {t('report.smsButton')}
        </button>
      </div>
    )
  }

  return (
    <div className="report-section sms-section">
      <form className="sms-form" onSubmit={handleSubmit}>
        <div className="field-row">
          <div className="field">
            <label htmlFor="sms-phone">{t('report.smsPhoneLabel')}</label>
            <input
              id="sms-phone"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder={t('report.smsPhonePlaceholder')}
            />
          </div>
          <div className="field">
            <label htmlFor="sms-weeks">{t('report.smsWeeksLabel')}</label>
            <input
              id="sms-weeks"
              type="number"
              min={0}
              max={52}
              value={weeks}
              onChange={(e) => setWeeks(e.target.value)}
            />
          </div>
        </div>

        <div className="actions">
          <button type="submit" className="primary" disabled={sending}>
            {sending ? (
              <>
                <span className="spinner" />
                {t('report.smsSending')}
              </>
            ) : (
              <>
                <MessageSquare />
                {t('report.smsSubmit')}
              </>
            )}
          </button>
          <button type="button" className="ghost" onClick={() => setOpen(false)}>
            {t('report.smsCancel')}
          </button>
        </div>

        {error && (
          <div className="error-box">
            <AlertCircle />
            <span>{error}</span>
          </div>
        )}

        {result && (
          <div className="success-box">
            <CheckCircle2 />
            <span>
              {t('report.smsSuccess', { date: new Date(result.appointment_date).toLocaleDateString() })}
            </span>
          </div>
        )}
      </form>
    </div>
  )
}

export default function ReportView({ report, similarCases, loading }) {
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
      <SimilarCasesList cases={similarCases} />
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

      <SmsAppointmentForm report={report} />
    </div>
  )
}
