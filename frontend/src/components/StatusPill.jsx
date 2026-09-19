import { useEffect, useState } from 'react'
import { CircleDot, Wifi, WifiOff } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'
import { checkHealth } from '../lib/api'

export default function StatusPill() {
  const { t } = useTranslation()
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    checkHealth()
      .then(() => setStatus('ok'))
      .catch(() => setStatus('down'))
  }, [])

  const label = status === 'ok' ? t('status.ok') : status === 'down' ? t('status.down') : t('status.checking')

  const Icon = status === 'ok' ? Wifi : status === 'down' ? WifiOff : CircleDot

  return (
    <div className={`status-pill ${status}`}>
      <Icon />
      <span>{label}</span>
    </div>
  )
}
