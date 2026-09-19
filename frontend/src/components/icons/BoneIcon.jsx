export default function BoneIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
      <line
        x1="7.3"
        y1="17.6"
        x2="16.7"
        y2="6.4"
        stroke="currentColor"
        strokeWidth="4.4"
        strokeLinecap="round"
      />
      <circle cx="7.34" cy="20.04" r="2.5" fill="currentColor" />
      <circle cx="4.66" cy="17.36" r="2.5" fill="currentColor" />
      <circle cx="19.34" cy="6.64" r="2.5" fill="currentColor" />
      <circle cx="16.66" cy="3.96" r="2.5" fill="currentColor" />
      <polyline
        points="13.84,13.84 12.21,13.06 11.79,10.94 10.16,10.16"
        stroke="var(--brand-glow, #2dd4bf)"
        strokeWidth="1.15"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
