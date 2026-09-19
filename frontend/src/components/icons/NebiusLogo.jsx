export default function NebiusLogo(props) {
  return (
    <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
      <rect width="32" height="32" rx="9" fill="#E4FA3D" />
      <path
        d="M9 6 L9 22 M23 6 L23 22 M9 6 C9 20 16 30 16 22 C16 14 23 20 23 6"
        stroke="#102A3B"
        strokeWidth="4.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
