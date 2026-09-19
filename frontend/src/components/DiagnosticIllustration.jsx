import { CheckCircle2 } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'
import tibiaFibulaXray from '../assets/img/tibia-fibula-xray.png'

export default function DiagnosticIllustration() {
  const { t } = useTranslation()

  return (
    <div className="diagnostic-illustration">
      <div className="diagnostic-frame">
        <div className="diagnostic-frame-bar">
          <span className="diagnostic-frame-dot diagnostic-frame-dot-red" />
          <span className="diagnostic-frame-dot diagnostic-frame-dot-amber" />
          <span className="diagnostic-frame-dot diagnostic-frame-dot-green" />
          <span className="diagnostic-frame-label">RX · 014</span>
        </div>

        <div className="diagnostic-film">
          <img src={tibiaFibulaXray} alt={t('landing.illustrationAlt')} />
          <span className="diagnostic-marker" />
          <span className="diagnostic-scan" />
        </div>
      </div>

      <div className="diagnostic-chip diagnostic-chip-match">
        <span className="diagnostic-chip-icon diagnostic-chip-icon-ok">
          <CheckCircle2 />
        </span>
        <span>{t('landing.illustrationMatches')}</span>
      </div>
    </div>
  )
}
