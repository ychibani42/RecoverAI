import { CheckCircle2, ScanSearch } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'

export function SimilarCasesIllustration({ title }) {
  const { t } = useTranslation()

  return (
    <div className="diagnostic-illustration">
      <svg viewBox="0 0 440 300" role="img" aria-label={title}>
        <defs>
          <linearGradient id="sc-screen" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#0c2e2c" />
            <stop offset="100%" stopColor="#155e56" />
          </linearGradient>
          <linearGradient id="sc-scan" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(255,255,255,0)" />
            <stop offset="50%" stopColor="rgba(255,255,255,0.32)" />
            <stop offset="100%" stopColor="rgba(255,255,255,0)" />
          </linearGradient>
        </defs>

        <rect x="0" y="0" width="440" height="300" rx="28" fill="#0a2523" />
        <rect x="10" y="10" width="420" height="280" rx="20" fill="url(#sc-screen)" />

        <circle cx="32" cy="32" r="4" fill="#f87171" opacity="0.85" />
        <circle cx="46" cy="32" r="4" fill="#fbbf24" opacity="0.85" />
        <circle cx="60" cy="32" r="4" fill="#4ade80" opacity="0.85" />

        {[
          { x: 44, y: 66, hi: true },
          { x: 172, y: 66, hi: false },
          { x: 300, y: 66, hi: true },
          { x: 44, y: 176, hi: false },
          { x: 172, y: 176, hi: true },
          { x: 300, y: 176, hi: false },
        ].map(({ x, y, hi }) => (
          <g key={`${x}-${y}`}>
            <rect
              x={x}
              y={y}
              width="96"
              height="72"
              rx="10"
              fill="rgba(255,255,255,0.06)"
              stroke={hi ? '#5eead4' : 'rgba(255,255,255,0.18)'}
              strokeWidth={hi ? 2 : 1}
            />
            <path
              d={`M${x + 30} ${y + 54} C${x + 27} ${y + 38}, ${x + 26} ${y + 24}, ${x + 34} ${y + 16}`}
              stroke="rgba(255,255,255,0.75)"
              strokeWidth="3"
              strokeLinecap="round"
              fill="none"
            />
            <path
              d={`M${x + 62} ${y + 54} C${x + 65} ${y + 38}, ${x + 66} ${y + 24}, ${x + 58} ${y + 16}`}
              stroke="rgba(255,255,255,0.75)"
              strokeWidth="3"
              strokeLinecap="round"
              fill="none"
            />
          </g>
        ))}

        <g stroke="#5eead4" strokeWidth="1.5" strokeDasharray="3 4" opacity="0.85">
          <line x1="140" y1="102" x2="172" y2="102" />
          <line x1="268" y1="212" x2="220" y2="102" />
        </g>

        <circle cx="92" cy="102" r="26" fill="none" stroke="#14b8a6" strokeWidth="2" strokeDasharray="4 4">
          <animateTransform attributeName="transform" type="rotate" from="0 92 102" to="360 92 102" dur="9s" repeatCount="indefinite" />
        </circle>
        <line x1="110" y1="120" x2="122" y2="132" stroke="#14b8a6" strokeWidth="4" strokeLinecap="round" />

        <rect x="10" y="10" width="420" height="50" fill="url(#sc-scan)">
          <animate attributeName="y" values="10;240;10" dur="4.5s" repeatCount="indefinite" />
        </rect>
      </svg>

      <div className="diagnostic-chip diagnostic-chip-lab">
        <span className="diagnostic-chip-icon">
          <ScanSearch />
        </span>
        <div>
          <span>{t('landing.featureChipScanning')}</span>
        </div>
      </div>

      <div className="diagnostic-chip diagnostic-chip-match">
        <span className="diagnostic-chip-icon diagnostic-chip-icon-ok">
          <CheckCircle2 />
        </span>
        <span>{t('landing.featureChipMatch')}</span>
      </div>
    </div>
  )
}

export function VectorEngineIllustration({ title }) {
  const { t } = useTranslation()

  const nodes = [
    { x: 90, y: 74 },
    { x: 60, y: 150 },
    { x: 110, y: 218 },
    { x: 330, y: 62 },
    { x: 362, y: 138 },
    { x: 316, y: 214 },
    { x: 150, y: 96 },
    { x: 268, y: 176 },
  ]

  return (
    <div className="diagnostic-illustration">
      <svg viewBox="0 0 440 300" role="img" aria-label={title}>
        <defs>
          <linearGradient id="ve-screen" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#0c2e2c" />
            <stop offset="100%" stopColor="#155e56" />
          </linearGradient>
          <radialGradient id="ve-core" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#ccfbf1" />
            <stop offset="100%" stopColor="#5eead4" />
          </radialGradient>
        </defs>

        <rect x="0" y="0" width="440" height="300" rx="28" fill="#0a2523" />
        <rect x="10" y="10" width="420" height="280" rx="20" fill="url(#ve-screen)" />

        <circle cx="32" cy="32" r="4" fill="#f87171" opacity="0.85" />
        <circle cx="46" cy="32" r="4" fill="#fbbf24" opacity="0.85" />
        <circle cx="60" cy="32" r="4" fill="#4ade80" opacity="0.85" />

        <g opacity="0.1" stroke="#ffffff" strokeWidth="1">
          <line x1="10" y1="150" x2="430" y2="150" />
          <line x1="220" y1="50" x2="220" y2="290" />
        </g>

        <g stroke="rgba(94,234,212,0.55)" strokeWidth="1.4">
          {nodes.map(({ x, y }) => (
            <line key={`${x}-${y}`} x1="220" y1="150" x2={x} y2={y} />
          ))}
        </g>

        {nodes.map(({ x, y }, i) => (
          <circle key={`${x}-${y}`} cx={x} cy={y} r="7" fill="rgba(255,255,255,0.85)" opacity={i % 2 === 0 ? 1 : 0.55} />
        ))}

        <circle cx="220" cy="150" r="30" fill="none" stroke="#14b8a6" strokeWidth="2" strokeDasharray="5 5">
          <animateTransform attributeName="transform" type="rotate" from="0 220 150" to="360 220 150" dur="11s" repeatCount="indefinite" />
        </circle>
        <circle cx="220" cy="150" r="13" fill="url(#ve-core)" />
      </svg>

      <div className="diagnostic-chip diagnostic-chip-lab">
        <span className="diagnostic-chip-icon">
          <ScanSearch />
        </span>
        <div>
          <span>{t('landing.featureChipFilters')}</span>
        </div>
      </div>

      <div className="diagnostic-chip diagnostic-chip-match">
        <span className="diagnostic-chip-icon diagnostic-chip-icon-ok">
          <CheckCircle2 />
        </span>
        <span>{t('landing.featureChipNeighbors')}</span>
      </div>
    </div>
  )
}

export function ReportIllustration({ title }) {
  const { t } = useTranslation()

  return (
    <div className="diagnostic-illustration">
      <svg viewBox="0 0 440 300" role="img" aria-label={title}>
        <defs>
          <linearGradient id="rp-screen" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#0c2e2c" />
            <stop offset="100%" stopColor="#155e56" />
          </linearGradient>
        </defs>

        <rect x="0" y="0" width="440" height="300" rx="28" fill="#0a2523" />
        <rect x="10" y="10" width="420" height="280" rx="20" fill="url(#rp-screen)" />

        <circle cx="32" cy="32" r="4" fill="#f87171" opacity="0.85" />
        <circle cx="46" cy="32" r="4" fill="#fbbf24" opacity="0.85" />
        <circle cx="60" cy="32" r="4" fill="#4ade80" opacity="0.85" />

        <rect x="40" y="58" width="200" height="212" rx="12" fill="rgba(255,255,255,0.07)" stroke="rgba(255,255,255,0.2)" />
        <rect x="60" y="78" width="120" height="12" rx="6" fill="rgba(255,255,255,0.55)" />
        {[110, 132, 154, 176, 198].map((y, i) => (
          <rect key={y} x="60" y={y} width={i === 4 ? 90 : 160} height="8" rx="4" fill="rgba(255,255,255,0.28)">
            <animate attributeName="width" values={`0;${i === 4 ? 90 : 160}`} dur="1.6s" begin={`${i * 0.25}s`} fill="freeze" />
          </rect>
        ))}
        <rect x="60" y="228" width="160" height="24" rx="8" fill="rgba(20,184,166,0.35)" stroke="#5eead4" />
        <text x="70" y="244" fill="#ccfbf1" fontSize="11" fontFamily="monospace">
          {t('landing.featureReportBadge')}
        </text>

        <g transform="translate(276,70)">
          {[0, 1, 2].map((i) => (
            <g key={i} transform={`translate(0, ${i * 62})`}>
              <line x1="10" y1="0" x2="10" y2="62" stroke="rgba(255,255,255,0.2)" />
              <circle cx="10" cy="0" r="9" fill={i < 2 ? '#4ade80' : 'rgba(255,255,255,0.9)'} />
              {i < 2 && (
                <path d="M6 0 L9 3 L15 -4" stroke="#083330" strokeWidth="1.6" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              )}
              <rect x="26" y="-8" width="120" height="16" rx="6" fill="rgba(255,255,255,0.12)" />
            </g>
          ))}
        </g>
      </svg>

      <div className="diagnostic-chip diagnostic-chip-lab">
        <span className="diagnostic-chip-icon">
          <ScanSearch />
        </span>
        <div>
          <span>{t('landing.featureChipSources')}</span>
        </div>
      </div>

      <div className="diagnostic-chip diagnostic-chip-match">
        <span className="diagnostic-chip-icon diagnostic-chip-icon-ok">
          <CheckCircle2 />
        </span>
        <span>{t('landing.featureChipReady')}</span>
      </div>
    </div>
  )
}

export const FEATURE_ILLUSTRATIONS = [SimilarCasesIllustration, VectorEngineIllustration, ReportIllustration]
