import { useState } from 'react'
import { ArrowLeft, ClipboardList, ShieldCheck, UserPlus, Users } from 'lucide-react'
import './App.css'
import './Landing.css'
import BoneIcon from './components/icons/BoneIcon'
import Landing from './components/Landing'
import LanguageSelector from './components/LanguageSelector'
import PatientForm from './components/PatientForm'
import PatientsTable from './components/PatientsTable'
import ReportView from './components/ReportView'
import { useTranslation } from './i18n/I18nContext'
import { requestReport } from './lib/api'

export default function App() {
  const { t } = useTranslation()
  const [view, setView] = useState('landing')
  const [report, setReport] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async ({ reportText, files, topK }) => {
    setSubmitting(true)
    setError('')
    setReport(null)
    try {
      const result = await requestReport({ reportText, files, topK })
      setReport(result)
    } catch (err) {
      setError(t('app.errorApiContact', { message: err.message }))
    } finally {
      setSubmitting(false)
    }
  }

  if (view === 'landing') {
    return <Landing onEnter={() => setView('workspace')} />
  }

  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <button type="button" className="back-link" onClick={() => setView('landing')}>
            <ArrowLeft />
          </button>
          <div className="logo-mark">
            <BoneIcon />
          </div>
          <div>
            <h1>Recover IA</h1>
            <p>{t('app.subtitle')}</p>
          </div>
          <div className="topbar-lang">
            <LanguageSelector />
          </div>
        </div>
        <div className="topbar-badges">
          <button
            type="button"
            className={`topbar-badge topbar-nav-btn ${view === 'workspace' ? 'active' : ''}`}
            onClick={() => setView('workspace')}
          >
            <ClipboardList />
            {t('card.newPatientTitle')}
          </button>
          <button
            type="button"
            className={`topbar-badge topbar-nav-btn ${view === 'patients' ? 'active' : ''}`}
            onClick={() => setView('patients')}
          >
            <Users />
            {t('patients.navLabel')}
          </button>
        </div>
      </header>

      {view === 'patients' ? (
        <main className="patients-main">
          <section className="card">
            <div className="card-header">
              <span className="card-icon">
                <Users />
              </span>
              <h2>{t('patients.title')}</h2>
            </div>
            <p className="card-hint">{t('patients.hint')}</p>
            <PatientsTable />
          </section>
        </main>
      ) : (
        <main>
          <section className="card">
            <div className="card-header">
              <span className="card-icon">
                <UserPlus />
              </span>
              <h2>{t('card.newPatientTitle')}</h2>
            </div>
            <p className="card-hint">{t('card.newPatientHint')}</p>
            <PatientForm onSubmit={handleSubmit} submitting={submitting} error={error} />
          </section>

          <section className="card">
            <div className="card-header">
              <span className="card-icon">
                <ClipboardList />
              </span>
              <h2>{t('card.reportTitle')}</h2>
            </div>
            <p className="card-hint">{t('card.reportHint')}</p>
            <ReportView report={report} loading={submitting} />
          </section>
        </main>
      )}

      <footer>
        <ShieldCheck />
        <span>{t('footer.disclaimer')}</span>
      </footer>
    </>
  )
}
