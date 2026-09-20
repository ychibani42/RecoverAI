import { useEffect, useRef, useState } from 'react'
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  ClipboardList,
  Clock,
  Download,
  HeartPulse,
  MessageSquare,
  Salad,
  Scale,
  Search,
  Stethoscope,
} from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'
import { sendAppointmentSms } from '../lib/api'
import { renderBoldText } from '../lib/markdownBold'
import NeighborsMap from './NeighborsMap'
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
      <p>{renderBoldText(value)}</p>
    </div>
  )
}

function KeyFactors({ factors }) {
  const { t } = useTranslation()
  if (!factors || factors.length === 0) return null

  return (
    <div className="report-section key-factors">
      <div className="report-section-header">
        <span className="section-icon">
          <Scale />
        </span>
        <h3>{t('report.keyFactorsTitle')}</h3>
      </div>
      <p className="card-hint">{t('report.keyFactorsHint')}</p>
      <ul className="key-factors-list">
        {factors.map((f) => (
          <li key={f.factor} className="key-factor-item">
            <div className="key-factor-header">
              <strong>{f.factor}</strong>
              <span className="badge">{f.valor_paciente}</span>
              <span className="badge key-factor-weight">
                {t('report.weightLabel')}: {(f.peso * 100).toFixed(0)}%
              </span>
            </div>
            <p>{renderBoldText(f.justificacion)}</p>
          </li>
        ))}
      </ul>
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

function DownloadPdfButton({ targetRef }) {
  const { t } = useTranslation()
  const [generating, setGenerating] = useState(false)

  const handleDownload = async () => {
    if (!targetRef.current || generating) return
    setGenerating(true)
    try {
      const { default: html2pdf } = await import('html2pdf.js')
      await html2pdf()
        .set({
          margin: 10,
          filename: `recover-ia-informe-${new Date().toISOString().slice(0, 10)}.pdf`,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2, useCORS: true },
          jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
          pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
        })
        .from(targetRef.current)
        .save()
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="report-section pdf-section">
      <button type="button" className="ghost" onClick={handleDownload} disabled={generating}>
        {generating ? <span className="spinner" /> : <Download />}
        {generating ? t('report.downloadPdfGenerating') : t('report.downloadPdfButton')}
      </button>
    </div>
  )
}

export default function ReportView({ report, similarCases, loading }) {
  const { t } = useTranslation()
  const printableRef = useRef(null)

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
      <div ref={printableRef} className="report-printable">
        <Section icon={Search} title={t('report.summary')} value={report.resumen_casos_similares} />
        <SimilarCasesList cases={similarCases} />
        <Section icon={Stethoscope} title={t('report.treatment')} value={report.tratamiento_recomendado} />
        <KeyFactors factors={report.factores_clave} />

        <div className="report-section">
          <div className="report-section-header">
            <span className="section-icon">
              <Clock />
            </span>
            <h3>{t('report.recoveryTime')}</h3>
          </div>
          <span className="badge">
            <Clock />
            {renderBoldText(report.tiempo_recuperacion_estimado)}
          </span>
        </div>

        <Section icon={Salad} title={t('report.diet')} value={report.dieta_recomendada} />
        <Section icon={HeartPulse} title={t('report.habits')} value={report.habitos_salud_recomendados} />

        <div className="report-section">
          <div className="warning-box">
            <AlertTriangle />
            <span>{renderBoldText(report.advertencia)}</span>
          </div>
        </div>
      </div>

      <div className="report-actions-row">
        <DownloadPdfButton targetRef={printableRef} />
        <SmsAppointmentForm report={report} />
        <NeighborsMap cases={similarCases} />
      </div>
    </div>
  )
}
