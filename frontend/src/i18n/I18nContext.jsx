import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { DEFAULT_LANGUAGE, LANGUAGES, TRANSLATIONS } from './translations'

const STORAGE_KEY = 'recover-ia-lang'
const LANGUAGE_CODES = LANGUAGES.map((l) => l.code)

function detectInitialLanguage() {
  if (typeof window === 'undefined') return DEFAULT_LANGUAGE
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY)
    if (stored && LANGUAGE_CODES.includes(stored)) return stored
  } catch {
    // localStorage unavailable, ignore
  }
  const browserLang = window.navigator?.language?.slice(0, 2)
  if (browserLang && LANGUAGE_CODES.includes(browserLang)) return browserLang
  return DEFAULT_LANGUAGE
}

function resolve(dict, key) {
  return key.split('.').reduce((acc, part) => (acc == null ? acc : acc[part]), dict)
}

const I18nContext = createContext(null)

export function I18nProvider({ children }) {
  const [language, setLanguageState] = useState(detectInitialLanguage)

  const setLanguage = useCallback((code) => {
    if (!LANGUAGE_CODES.includes(code)) return
    setLanguageState(code)
    try {
      window.localStorage.setItem(STORAGE_KEY, code)
    } catch {
      // localStorage unavailable, ignore
    }
  }, [])

  const t = useCallback(
    (key, vars) => {
      const dict = TRANSLATIONS[language] || TRANSLATIONS[DEFAULT_LANGUAGE]
      let value = resolve(dict, key)
      if (value === undefined) value = resolve(TRANSLATIONS[DEFAULT_LANGUAGE], key)
      if (value === undefined) return key
      if (typeof value === 'string' && vars) {
        return Object.entries(vars).reduce((str, [k, v]) => str.replaceAll(`{${k}}`, v), value)
      }
      return value
    },
    [language],
  )

  const value = useMemo(() => ({ language, setLanguage, t, languages: LANGUAGES }), [language, setLanguage, t])

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useTranslation() {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useTranslation must be used within an I18nProvider')
  return ctx
}
