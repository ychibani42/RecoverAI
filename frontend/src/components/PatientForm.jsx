import { useRef, useState } from 'react'
import { AlertCircle, FileText, Mic, Sparkles, Square, Wand2 } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'
import { transcribeAudio } from '../lib/api'
import FileDropzone from './FileDropzone'
import StatusPill from './StatusPill'

export default function PatientForm({ onSubmit, submitting, error }) {
  const { t, language } = useTranslation()
  const [reportText, setReportText] = useState('')
  const [files, setFiles] = useState([])
  const [topK, setTopK] = useState(5)
  const [validationError, setValidationError] = useState('')
  const [recording, setRecording] = useState(false)
  const [transcribing, setTranscribing] = useState(false)
  const [dictationError, setDictationError] = useState('')
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  const useSample = () => {
    setReportText(t('form.sampleReport'))
  }

  const startDictation = async () => {
    setDictationError('')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop())
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setTranscribing(true)
        try {
          const { text } = await transcribeAudio({ blob, language })
          setReportText((prev) => (prev.trim() ? `${prev.trim()} ${text}` : text))
        } catch {
          setDictationError(t('form.dictationError'))
        } finally {
          setTranscribing(false)
        }
      }
      mediaRecorderRef.current = recorder
      recorder.start()
      setRecording(true)
    } catch {
      setDictationError(t('form.dictationPermissionError'))
    }
  }

  const stopDictation = () => {
    mediaRecorderRef.current?.stop()
    setRecording(false)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const trimmed = reportText.trim()
    if (!trimmed) {
      setValidationError(t('form.validationReportRequired'))
      return
    }
    setValidationError('')
    onSubmit({ reportText: trimmed, files, topK })
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="field">
        <div className="field-label-row">
          <label htmlFor="report-text">
            <FileText />
            {t('form.reportLabel')}
          </label>
          <button
            type="button"
            className={`dictation-button${recording ? ' recording' : ''}`}
            onClick={recording ? stopDictation : startDictation}
            disabled={transcribing}
            title={t(recording ? 'form.dictationStop' : 'form.dictationStart')}
          >
            {recording ? <Square /> : <Mic />}
            {transcribing ? t('form.dictationTranscribing') : t(recording ? 'form.dictationStop' : 'form.dictationStart')}
          </button>
        </div>
        <textarea
          id="report-text"
          rows={6}
          value={reportText}
          onChange={(e) => setReportText(e.target.value)}
          placeholder={t('form.reportPlaceholder')}
        />
        {dictationError && (
          <div className="error-box">
            <AlertCircle />
            <span>{dictationError}</span>
          </div>
        )}
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
