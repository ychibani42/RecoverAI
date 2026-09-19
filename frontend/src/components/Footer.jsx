import { ShieldCheck } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'
import NebiusLogo from './icons/NebiusLogo'
import SlngLogo from './icons/SlngLogo'
import VonageLogo from './icons/VonageLogo'

export default function Footer() {
  const { t } = useTranslation()

  return (
    <footer className="landing-footer">
      <div className="landing-footer-row">
        <ShieldCheck />
        <span>{t('footer.disclaimer')}</span>
      </div>
      <div className="landing-footer-row landing-footer-credit">
        <span>{t('footer.techBy')}</span>
        <div className="landing-footer-brands">
          <span className="landing-footer-brand">
            <NebiusLogo />
            Nebius
          </span>
          <span className="landing-footer-brand landing-footer-brand-mono">
            <VonageLogo />
            VONAGE
          </span>
          <span className="landing-footer-brand landing-footer-brand-mono">
            <SlngLogo />
            SLNG
          </span>
        </div>
      </div>
    </footer>
  )
}
