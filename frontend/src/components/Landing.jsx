import { ArrowRight, Brain, Database, LogOut, ScanSearch, ShieldCheck } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'
import DiagnosticIllustration from './DiagnosticIllustration'
import { FEATURE_ILLUSTRATIONS } from './FeatureIllustrations'
import Footer from './Footer'
import BoneIcon from './icons/BoneIcon'
import LanguageSelector from './LanguageSelector'

const FEATURE_ICONS = [ScanSearch, Database, Brain]

export default function Landing({ onEnter, onLogout }) {
  const { t } = useTranslation()
  const features = t('landing.features')

  return (
    <div className="landing">
      <header className="landing-hero">
        <div className="landing-hero-decor" aria-hidden="true"></div>
        <div className="landing-hero-top">
          <LanguageSelector />
          {onLogout && (
            <button type="button" className="back-link" title={t('auth.logout')} onClick={onLogout}>
              <LogOut />
            </button>
          )}
        </div>
        <div className="landing-hero-inner">
          <div className="landing-hero-text">
            <div className="landing-logo">
              <span className="logo-mark">
                <BoneIcon />
              </span>
              <span className="landing-logo-text">Recover IA</span>
            </div>

            <h1>
              {t('landing.heroTitlePrefix')} <span>{t('landing.heroTitleHighlight')}</span>
            </h1>
            <p className="landing-subtitle">{t('landing.heroSubtitle')}</p>

            <div className="landing-cta">
              <button type="button" className="primary" onClick={onEnter}>
                {t('landing.ctaEnter')}
                <ArrowRight />
              </button>
              <span className="landing-cta-hint">
                <ShieldCheck />
                {t('app.badgeSupport')}
              </span>
            </div>
          </div>

          <div className="landing-hero-visual">
            <DiagnosticIllustration />
          </div>
        </div>
      </header>

      <main className="landing-main">
        <section className="landing-section">
          <h2>{t('landing.howItWorks')}</h2>
          <div className="landing-features">
            {features.map(({ title, description }, i) => {
              const Icon = FEATURE_ICONS[i]
              const Illustration = FEATURE_ILLUSTRATIONS[i]
              return (
                <div className={`landing-feature-row${i % 2 === 1 ? ' is-reverse' : ''}`} key={title}>
                  <div className="landing-feature-visual">
                    <Illustration title={title} />
                  </div>
                  <div className="landing-feature-content">
                    <span className="landing-feature-step">0{i + 1}</span>
                    <span className="card-icon">
                      <Icon />
                    </span>
                    <h3>{title}</h3>
                    <p>{description}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
