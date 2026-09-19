function FlagBase({ children, title }) {
  return (
    <svg className="flag-icon" viewBox="0 0 30 20" role="img" aria-label={title}>
      {children}
    </svg>
  )
}

export function FlagES({ title = 'Español' }) {
  return (
    <FlagBase title={title}>
      <rect width="30" height="20" fill="#AA151B" />
      <rect y="5" width="30" height="10" fill="#F1BF00" />
    </FlagBase>
  )
}

export function FlagGB({ title = 'English' }) {
  return (
    <FlagBase title={title}>
      <rect width="30" height="20" fill="#012169" />
      <path d="M0,0 30,20 M30,0 0,20" stroke="#FFF" strokeWidth="4" />
      <path d="M0,0 30,20 M30,0 0,20" stroke="#C8102E" strokeWidth="2" />
      <path d="M15,0 15,20 M0,10 30,10" stroke="#FFF" strokeWidth="6" />
      <path d="M15,0 15,20 M0,10 30,10" stroke="#C8102E" strokeWidth="3.5" />
    </FlagBase>
  )
}

export function FlagFR({ title = 'Français' }) {
  return (
    <FlagBase title={title}>
      <rect width="10" height="20" fill="#0055A4" />
      <rect x="10" width="10" height="20" fill="#FFF" />
      <rect x="20" width="10" height="20" fill="#EF4135" />
    </FlagBase>
  )
}

export function FlagCA({ title = 'Català' }) {
  return (
    <FlagBase title={title}>
      <rect width="30" height="20" fill="#FCDD09" />
      {[0, 1, 2, 3].map((i) => (
        <rect key={i} y={2 + i * 4} width="30" height="2" fill="#DA121A" />
      ))}
    </FlagBase>
  )
}

export function FlagDE({ title = 'Deutsch' }) {
  return (
    <FlagBase title={title}>
      <rect width="30" height="6.67" y="0" fill="#000" />
      <rect width="30" height="6.67" y="6.67" fill="#DD0000" />
      <rect width="30" height="6.67" y="13.33" fill="#FFCE00" />
    </FlagBase>
  )
}

export const FLAGS = {
  es: FlagES,
  en: FlagGB,
  fr: FlagFR,
  ca: FlagCA,
  de: FlagDE,
}
