const FIELD_LABELS = {
  file: 'Booklet PDF',
  full_name: 'Full name',
  password: 'Password',
  question_paper: 'Question paper PDF',
  subject_id: 'Subject',
  usn: 'USN',
}

function formatValidationError(error) {
  const field = error.loc?.at(-1)
  const label = FIELD_LABELS[field] || (field ? String(field).replaceAll('_', ' ') : '')

  if (error.type === 'missing') return `${label || 'This field'} is required.`
  if (error.type === 'string_too_short' && field === 'password') {
    return 'Password must be at least 8 characters.'
  }
  if (error.type === 'string_too_long' && field === 'password') {
    return 'Password must not exceed 72 UTF-8 bytes.'
  }
  if (error.type === 'string_pattern_mismatch' && field === 'usn') {
    return 'Enter a valid USN, for example 4JD23IS107.'
  }
  if (error.type === 'string_pattern_mismatch' && field === 'full_name') {
    return 'Use 2–100 letters, spaces, apostrophes, periods, or hyphens.'
  }

  const message = String(error.msg || 'is invalid').replace(/^Value error,\s*/, '')
  return label && !message.toLowerCase().startsWith(label.toLowerCase())
    ? `${label}: ${message}`
    : message
}

export function getApiErrorMessage(error, fallback = 'Please try again.') {
  const detail = error?.response?.data?.detail

  if (typeof detail === 'string' && detail.trim()) return detail
  if (Array.isArray(detail)) {
    const messages = [...new Set(detail.map(formatValidationError))]
    if (messages.length) return messages.join(' ')
  }
  if (typeof detail === 'object' && detail !== null) {
    if (typeof detail.message === 'string') return detail.message
    if (typeof detail.msg === 'string') return detail.msg
  }
  if (!error?.response && error?.message === 'Network Error') {
    return 'Unable to connect to the server. Check your connection and try again.'
  }
  return error?.message || fallback
}
