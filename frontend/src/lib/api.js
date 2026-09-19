export const API_BASE =
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : `${window.location.protocol}//${window.location.hostname}:8000`

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2500) })
  if (!res.ok) throw new Error('unhealthy')
  return true
}

export async function requestReport({ reportText, files, topK }) {
  const formData = new FormData()
  formData.append('medical_report_text', reportText)
  formData.append('top_k', String(topK || 5))
  files.forEach((file) => formData.append('additional_files', file))

  const res = await fetch(`${API_BASE}/cases/report`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `Error ${res.status}`)
  }

  return res.json()
}

export async function sendAppointmentSms({ phone, weeks }) {
  const res = await fetch(`${API_BASE}/sms/appointment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, weeks }),
  })

  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `Error ${res.status}`)
  }

  return res.json()
}

export async function getPatients() {
  const res = await fetch(`${API_BASE}/patients`, { signal: AbortSignal.timeout(10000) })
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `Error ${res.status}`)
  }
  return res.json()
}
