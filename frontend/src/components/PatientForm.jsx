import { useState } from 'react'
import { AlertCircle, FileText, FlaskConical, Sparkles, Wand2 } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'
import FileDropzone from './FileDropzone'
import StatusPill from './StatusPill'

export default function PatientForm({ onSubmit, submitting, error }) {
  const { t } = useTranslation()
  const [reportText, setReportText] = useState('')
  const [labText, setLabText] = useState('')
  const [files, setFiles] = useState([])
  const [topK, setTopK] = useState(5)
  const [validationError, setValidationError] = useState('')

  const useSample = () => {
    setReportText(t('form.sampleReport'))
    setLabText(t('form.sampleLabs'))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const trimmed = reportText.trim()
    if (!trimmed) {
      setValidationError(t('form.validationReportRequired'))
      return
    }
    setValidationError('')
    onSubmit({ reportText: trimmed, labText: labText.trim(), files, topK })
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="report-text">
          <FileText />
          {t('form.reportLabel')}
        </label>
        <textarea
          id="report-text"
          rows={6}
          value={reportText}
          onChange={(e) => setReportText(e.target.value)}
          placeholder={t('form.reportPlaceholder')}
        />
      </div>

      <div className="field">
        <label htmlFor="lab-text">
          <FlaskConical />
          {t('form.labsLabel')}
        </label>
        <textarea
          id="lab-text"
          rows={3}
          value={labText}
          onChange={(e) => setLabText(e.target.value)}
          placeholder={t('form.labsPlaceholder')}
        />
      </div>

      <div className="field">
        <label>{t('form.filesLabel')}</label>
        <FileDropzone files={files} onChange={setFiles} />
      </div>

      <div className="field-row">
        <div className="field">
          <label htmlFor="top-k">
            <Sparkles />
            {t('form.topKLabel')}
          </label>
          <input
            id="top-k"
            type="number"
            min={1}
            max={10}
            value={topK}
            onChange={(e) => setTopK(e.target.value)}
          />
        </div>
      </div>

      <div className="actions">
        <button type="submit" className="primary" disabled={submitting}>
          {submitting ? (
            <>
              <span className="spinner" />
              {t('form.submitLoading')}
            </>
          ) : (
            <>
              <Sparkles />
              {t('form.submitIdle')}
            </>
          )}
        </button>
        <button type="button" className="ghost" onClick={useSample}>
          <Wand2 />
          {t('form.useSample')}
        </button>
      </div>

      <StatusPill />

      {(validationError || error) && (
        <div className="error-box">
          <AlertCircle />
          <span>{validationError || error}</span>
        </div>
      )}
    </form>
  )
}
