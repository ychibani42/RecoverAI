import { useEffect, useState } from 'react'
import { ArrowLeft, ClipboardList, UserPlus, Users } from 'lucide-react'
import './App.css'
import './Landing.css'
import BoneIcon from './components/icons/BoneIcon'
import Footer from './components/Footer'
import Landing from './components/Landing'
import Login from './components/Login'
import PatientForm from './components/PatientForm'
import PatientsTable from './components/PatientsTable'
import ReportView from './components/ReportView'
import TopMenu from './components/TopMenu'
import { useTranslation } from './i18n/I18nContext'
import { clearToken, getToken, requestReport, UNAUTHORIZED_EVENT } from './lib/api'

export default function App() {
  const { t, language } = useTranslation()
  const [authenticated, setAuthenticated] = useState(() => !!getToken())
  const [view, setView] = useState('landing')
  const [report, setReport] = useState(null)
  const [similarCases, setSimilarCases] = useState([])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const handleUnauthorized = () => {
      setAuthenticated(false)
      setView('landing')
    }
    window.addEventListener(UNAUTHORIZED_EVENT, handleUnauthorized)
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, handleUnauthorized)
  }, [])

  const handleEnter = () => {
    setView(authenticated ? 'workspace' : 'login')
  }

  const handleLoginSuccess = () => {
    setAuthenticated(true)
    setView('workspace')
  }

  const handleSubmit = async ({ reportText, files, topK }) => {
    setSubmitting(true)
    setError('')
    setReport(null)
    setSimilarCases([])
    try {
      const result = await requestReport({ reportText, files, topK, language })
      setReport(result.report)
      setSimilarCases(result.similar_cases || [])
    } catch (err) {
      if (err.message !== 'unauthorized') {
        setError(t('app.errorApiContact', { message: err.message }))
      }
    } finally {
      setSubmitting(false)
    }
  }

  const handleLogout = () => {
    clearToken()
    setAuthenticated(false)
    setView('landing')
  }

  if (view === 'landing') {
    return (
      <Landing
        onEnter={handleEnter}
        authenticated={authenticated}
        onHome={() => setView('landing')}
        onLogin={() => setView('login')}
        onLogout={authenticated ? handleLogout : undefined}
      />
    )
  }

  if (view === 'login') {
    return <Login onSuccess={handleLoginSuccess} onHome={() => setView('landing')} />
  }

  return (
    <>
      <header className="topbar">
        <div className="topbar-decor" aria-hidden="true"></div>
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
            <TopMenu
              authenticated={authenticated}
              onHome={() => setView('landing')}
              onLogin={() => setView('login')}
              onLogout={handleLogout}
            />
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
            <ReportView report={report} similarCases={similarCases} loading={submitting} />
          </section>
        </main>
      )}

      <Footer />
    </>
  )
}
