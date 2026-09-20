const BOLD_PATTERN = /\*\*(.+?)\*\*/g

/**
 * Turns `**text**` markers from the LLM-generated report into <strong> spans
 * so the most clinically relevant parts of the text stand out visually and
 * in the exported PDF.
 */
export function renderBoldText(text) {
  if (!text) return text
  const parts = []
  let lastIndex = 0
  let match
  let key = 0

  while ((match = BOLD_PATTERN.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index))
    }
    parts.push(<strong key={key++}>{match[1]}</strong>)
    lastIndex = BOLD_PATTERN.lastIndex
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex))
  }

  return parts
}
