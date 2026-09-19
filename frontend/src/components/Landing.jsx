import { ArrowRight, Bone, Brain, Database, ScanSearch, ShieldCheck } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'
import DiagnosticIllustration from './DiagnosticIllustration'
import LanguageSelector from './LanguageSelector'

const FEATURE_ICONS = [ScanSearch, Database, Brain]

export default function Landing({ onEnter }) {
  const { t } = useTranslation()
  const features = t('landing.features')

  return (
    <div className="landing">
      <header className="landing-hero">
        <div className="landing-hero-top">
          <LanguageSelector />
        </div>
        <div className="landing-hero-inner">
          <div className="landing-hero-text">
            <div className="landing-logo">
              <span className="logo-mark">
                <Bone />
              </span>
              <span className="landing-logo-text">recovery-ia</span>
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
              return (
                <div className="landing-feature-card" key={title}>
                  <span className="card-icon">
                    <Icon />
                  </span>
                  <h3>{title}</h3>
                  <p>{description}</p>
                </div>
              )
            })}
          </div>
        </section>
      </main>

      <footer className="landing-footer">
        <ShieldCheck />
        <span>{t('footer.disclaimer')}</span>
      </footer>
    </div>
  )
}
