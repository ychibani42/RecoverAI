import { useEffect, useRef, useState } from 'react'
import { ChevronDown, Globe } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'
import { FLAGS } from './flags'

export default function LanguageSelector({ variant = 'light' }) {
  const { language, setLanguage, t, languages } = useTranslation()
  const [open, setOpen] = useState(false)
  const rootRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (rootRef.current && !rootRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const CurrentFlag = FLAGS[language]

  return (
    <div className={`language-selector ${variant}`} ref={rootRef}>
      <button
        type="button"
        className="language-selector-trigger"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={t('language.selectorLabel')}
      >
        <Globe className="language-selector-icon" />
        {CurrentFlag && <CurrentFlag />}
        <span className="language-selector-code">{language.toUpperCase()}</span>
        <ChevronDown className="language-selector-chevron" />
      </button>
      {open && (
        <ul className="language-selector-menu" role="listbox">
          {languages.map(({ code, label }) => {
            const Flag = FLAGS[code]
            return (
              <li key={code}>
                <button
                  type="button"
                  className={`language-selector-option${code === language ? ' active' : ''}`}
                  role="option"
                  aria-selected={code === language}
                  onClick={() => {
                    setLanguage(code)
                    setOpen(false)
                  }}
                >
                  {Flag && <Flag />}
                  <span>{label}</span>
                </button>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
