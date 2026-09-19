export const API_BASE =
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : `${window.location.protocol}//${window.location.hostname}:8000`

const TOKEN_KEY = 'recoveria_token'
export const UNAUTHORIZED_EVENT = 'recoveria:unauthorized'

export function getToken() {
  try {
    return window.sessionStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

function setToken(token) {
  try {
    window.sessionStorage.setItem(TOKEN_KEY, token)
  } catch {
    // sessionStorage unavailable, ignore
  }
}

export function clearToken() {
  try {
    window.sessionStorage.removeItem(TOKEN_KEY)
  } catch {
    // sessionStorage unavailable, ignore
  }
}

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function throwIfUnauthorized(res) {
  if (res.status === 401) {
    clearToken()
    window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
    throw new Error('unauthorized')
  }
}

export async function login(username, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })

  if (!res.ok) {
    throw new Error(res.status === 401 ? 'invalid_credentials' : `Error ${res.status}`)
  }

  const data = await res.json()
  setToken(data.access_token)
  return data
}

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2500) })
  if (!res.ok) throw new Error('unhealthy')
  return true
}

export async function requestReport({ reportText, files, topK, language }) {
  const formData = new FormData()
  formData.append('medical_report_text', reportText)
  formData.append('top_k', String(topK || 5))
  formData.append('language', language || 'es')
  files.forEach((file) => formData.append('additional_files', file))

  const res = await fetch(`${API_BASE}/cases/report`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData,
  })

  await throwIfUnauthorized(res)
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `Error ${res.status}`)
  }

  return res.json()
}

export async function sendAppointmentSms({ phone, weeks }) {
  const res = await fetch(`${API_BASE}/sms/appointment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ phone, weeks }),
  })

  await throwIfUnauthorized(res)
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `Error ${res.status}`)
  }

  return res.json()
}

export async function transcribeAudio({ blob, language }) {
  const formData = new FormData()
  formData.append('audio', blob, 'dictado.webm')
  formData.append('language', language || 'es')

  const res = await fetch(`${API_BASE}/transcription`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData,
  })

  await throwIfUnauthorized(res)
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `Error ${res.status}`)
  }

  return res.json()
}

export function imageUrl(relativePath) {
  if (!relativePath) return null
  return `${API_BASE}/images/${relativePath}`
}

export async function getPatients() {
  const res = await fetch(`${API_BASE}/patients`, {
    headers: authHeaders(),
    signal: AbortSignal.timeout(10000),
  })
  await throwIfUnauthorized(res)
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `Error ${res.status}`)
  }
  return res.json()
}
