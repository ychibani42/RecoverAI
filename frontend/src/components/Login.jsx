import { useState } from 'react'
import { AlertCircle, Lock, LogIn, User } from 'lucide-react'
import { login } from '../lib/api'
import { useTranslation } from '../i18n/I18nContext'
import TopMenu from './TopMenu'
import BoneIcon from './icons/BoneIcon'

export default function Login({ onSuccess, onHome }) {
  const { t } = useTranslation()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await login(username, password)
      onSuccess()
    } catch (err) {
      setError(
        err.message === 'invalid_credentials'
          ? t('auth.invalidCredentials')
          : t('auth.genericError', { message: err.message }),
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-page-top">
        <TopMenu authenticated={false} onHome={onHome} onLogin={() => {}} />
      </div>
      <div className="login-card card">
        <div className="login-logo">
          <span className="login-logo-mark">
            <BoneIcon />
          </span>
          <span className="login-logo-text">Recover IA</span>
        </div>

        <h2>{t('auth.title')}</h2>
        <p className="card-hint">{t('auth.subtitle')}</p>

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="login-username">
              <User />
              {t('auth.usernameLabel')}
            </label>
            <input
              id="login-username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
            />
          </div>

          <div className="field">
            <label htmlFor="login-password">
              <Lock />
              {t('auth.passwordLabel')}
            </label>
            <input
              id="login-password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div className="actions">
            <button type="submit" className="primary" disabled={submitting}>
              {submitting ? (
                <>
                  <span className="spinner" />
                  {t('auth.submitLoading')}
                </>
              ) : (
                <>
                  <LogIn />
                  {t('auth.submitIdle')}
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="error-box">
              <AlertCircle />
              <span>{error}</span>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}
