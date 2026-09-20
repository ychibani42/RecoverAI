import { useEffect, useRef, useState } from 'react'
import { ChevronDown, Globe, Home, LogIn, LogOut, Menu, Moon, Settings, Sun } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'
import { useTheme } from '../theme/ThemeContext'
import { FLAGS } from './flags'

export default function TopMenu({ authenticated, onHome, onLogin, onLogout, variant = 'light' }) {
  const { language, setLanguage, t, languages } = useTranslation()
  const { theme, setTheme } = useTheme()
  const [open, setOpen] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [languageOpen, setLanguageOpen] = useState(false)
  const [themeOpen, setThemeOpen] = useState(false)
  const rootRef = useRef(null)

  const closeAll = () => {
    setOpen(false)
    setSettingsOpen(false)
    setLanguageOpen(false)
    setThemeOpen(false)
  }

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (rootRef.current && !rootRef.current.contains(e.target)) closeAll()
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className={`top-menu ${variant}`} ref={rootRef}>
      <button
        type="button"
        className="back-link"
        onClick={() => (open ? closeAll() : setOpen(true))}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={t('menu.label')}
      >
        <Menu />
      </button>
      {open && (
        <ul className="top-menu-menu" role="menu">
          <li role="none">
            <button
              type="button"
              className="top-menu-item"
              role="menuitem"
              onClick={() => {
                onHome?.()
                closeAll()
              }}
            >
              <Home className="top-menu-item-icon" />
              <span>{t('menu.home')}</span>
            </button>
          </li>
          <li role="none">
            {authenticated ? (
              <button
                type="button"
                className="top-menu-item"
                role="menuitem"
                onClick={() => {
                  onLogout?.()
                  closeAll()
                }}
              >
                <LogOut className="top-menu-item-icon" />
                <span>{t('menu.logout')}</span>
              </button>
            ) : (
              <button
                type="button"
                className="top-menu-item"
                role="menuitem"
                onClick={() => {
                  onLogin?.()
                  closeAll()
                }}
              >
                <LogIn className="top-menu-item-icon" />
                <span>{t('menu.login')}</span>
              </button>
            )}
          </li>

          {authenticated && (
            <li role="none" className="top-menu-group">
              <button
                type="button"
                className="top-menu-item top-menu-section-toggle"
                role="menuitem"
                aria-expanded={settingsOpen}
                onClick={() => setSettingsOpen((o) => !o)}
              >
                <Settings className="top-menu-item-icon" />
                <span>{t('menu.settings')}</span>
                <ChevronDown className={`top-menu-chevron${settingsOpen ? ' open' : ''}`} />
              </button>

              {settingsOpen && (
                <ul className="top-menu-submenu" role="menu">
                  <li role="none" className="top-menu-subgroup">
                    <button
                      type="button"
                      className="top-menu-item top-menu-section-toggle"
                      role="menuitem"
                      aria-expanded={languageOpen}
                      onClick={() => setLanguageOpen((o) => !o)}
                    >
                      <Globe className="top-menu-item-icon" />
                      <span>{t('menu.language')}</span>
                      <ChevronDown className={`top-menu-chevron${languageOpen ? ' open' : ''}`} />
                    </button>
                    {languageOpen && (
                      <ul className="top-menu-submenu" role="menu">
                        {languages.map(({ code, label }) => {
                          const Flag = FLAGS[code]
                          return (
                            <li role="none" key={code}>
                              <button
                                type="button"
                                className={`top-menu-item${code === language ? ' active' : ''}`}
                                role="menuitemradio"
                                aria-checked={code === language}
                                onClick={() => {
                                  setLanguage(code)
                                  closeAll()
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
                  </li>

                  <li role="none" className="top-menu-subgroup">
                    <button
                      type="button"
                      className="top-menu-item top-menu-section-toggle"
                      role="menuitem"
                      aria-expanded={themeOpen}
                      onClick={() => setThemeOpen((o) => !o)}
                    >
                      {theme === 'dark' ? <Moon className="top-menu-item-icon" /> : <Sun className="top-menu-item-icon" />}
                      <span>{t('menu.theme')}</span>
                      <ChevronDown className={`top-menu-chevron${themeOpen ? ' open' : ''}`} />
                    </button>
                    {themeOpen && (
                      <ul className="top-menu-submenu" role="menu">
                        <li role="none">
                          <button
                            type="button"
                            className={`top-menu-item${theme === 'light' ? ' active' : ''}`}
                            role="menuitemradio"
                            aria-checked={theme === 'light'}
                            onClick={() => {
                              setTheme('light')
                              closeAll()
                            }}
                          >
                            <Sun className="top-menu-item-icon" />
                            <span>{t('menu.themeLight')}</span>
                          </button>
                        </li>
                        <li role="none">
                          <button
                            type="button"
                            className={`top-menu-item${theme === 'dark' ? ' active' : ''}`}
                            role="menuitemradio"
                            aria-checked={theme === 'dark'}
                            onClick={() => {
                              setTheme('dark')
                              closeAll()
                            }}
                          >
                            <Moon className="top-menu-item-icon" />
                            <span>{t('menu.themeDark')}</span>
                          </button>
                        </li>
                      </ul>
                    )}
                  </li>
                </ul>
              )}
            </li>
          )}
        </ul>
      )}
    </div>
  )
}
