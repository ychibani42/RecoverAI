import { CheckCircle2, FlaskConical } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'

export default function DiagnosticIllustration() {
  const { t } = useTranslation()

  return (
    <div className="diagnostic-illustration">
      <svg viewBox="0 0 440 340" role="img" aria-label={t('landing.illustrationAlt')}>
        <defs>
          <linearGradient id="di-screen" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#241146" />
            <stop offset="100%" stopColor="#3b1f78" />
          </linearGradient>
          <linearGradient id="di-scan" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(255,255,255,0)" />
            <stop offset="50%" stopColor="rgba(255,255,255,0.35)" />
            <stop offset="100%" stopColor="rgba(255,255,255,0)" />
          </linearGradient>
        </defs>

        <rect x="0" y="0" width="440" height="340" rx="28" fill="#2a1854" />
        <rect x="10" y="10" width="420" height="320" rx="20" fill="url(#di-screen)" />

        <circle cx="32" cy="32" r="4" fill="#f87171" opacity="0.85" />
        <circle cx="46" cy="32" r="4" fill="#fbbf24" opacity="0.85" />
        <circle cx="60" cy="32" r="4" fill="#4ade80" opacity="0.85" />
        <text x="408" y="37" fill="rgba(255,255,255,0.45)" fontSize="11" textAnchor="end" fontFamily="monospace">
          RX · 014
        </text>

        <g opacity="0.12" stroke="#ffffff" strokeWidth="1">
          <line x1="10" y1="80" x2="430" y2="80" />
          <line x1="10" y1="140" x2="430" y2="140" />
          <line x1="10" y1="200" x2="430" y2="200" />
          <line x1="10" y1="260" x2="430" y2="260" />
          <line x1="110" y1="50" x2="110" y2="330" />
          <line x1="220" y1="50" x2="220" y2="330" />
          <line x1="330" y1="50" x2="330" y2="330" />
        </g>

        <g stroke="rgba(255,255,255,0.9)" strokeWidth="7" strokeLinecap="round" fill="none">
          <path d="M195 300 C190 250, 188 200, 198 150" />
          <path d="M245 300 C248 250, 246 200, 232 150" />
          <path d="M198 150 C200 130, 208 118, 218 112" />
          <path d="M232 150 C230 130, 224 118, 218 112" />
          <path d="M215 112 L205 78" />
          <path d="M218 110 L214 74" />
          <path d="M222 111 L224 76" />
          <path d="M226 114 L233 82" />
          <path d="M210 111 L197 80" />
        </g>
        <g fill="rgba(255,255,255,0.9)">
          <circle cx="205" cy="72" r="4.5" />
          <circle cx="214" cy="68" r="4.5" />
          <circle cx="224" cy="70" r="4.5" />
          <circle cx="233" cy="76" r="4.5" />
          <circle cx="197" cy="78" r="4.5" />
        </g>

        <path d="M186 208 L206 200 L192 222 L212 216" stroke="#f87171" strokeWidth="3.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="198" cy="210" r="20" fill="none" stroke="#f87171" strokeWidth="2" strokeDasharray="4 4">
          <animateTransform attributeName="transform" type="rotate" from="0 198 210" to="360 198 210" dur="10s" repeatCount="indefinite" />
        </circle>

        <rect x="10" y="10" width="420" height="60" fill="url(#di-scan)">
          <animate attributeName="y" values="10;270;10" dur="4.5s" repeatCount="indefinite" />
        </rect>
      </svg>

      <div className="diagnostic-chip diagnostic-chip-lab">
        <span className="diagnostic-chip-icon">
          <FlaskConical />
        </span>
        <div>
          <strong>{t('landing.illustrationLabLabel')}</strong>
          <span>{t('landing.illustrationLabValue')}</span>
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
