const FIELD_LABELS = {
  name: 'Name',
  year: 'Year',
  month: 'Month',
  day: 'Day',
  hour: 'Hour',
  minute: 'Minute',
  lat: 'Latitude',
  lng: 'Longitude',
  tz_str: 'Timezone',
  city: 'City',
  nation: 'Country',
  houses_system: 'House system',
  zodiac_type: 'Zodiac type',
}

const SKIP_LOC_PARTS = new Set(['body', 'query', 'path', 'data', 'data2'])

export const joinList = (items) => {
  if (items.length === 1) return items[0]
  if (items.length === 2) return `${items[0]} and ${items[1]}`
  return `${items.slice(0, -1).join(', ')}, and ${items[items.length - 1]}`
}

const fieldLabelFromLoc = (loc) => {
  if (!Array.isArray(loc)) return ''
  const parts = loc.filter((part) => typeof part === 'string' && !SKIP_LOC_PARTS.has(part))
  const key = parts[parts.length - 1]
  return FIELD_LABELS[key] || key || ''
}

const formatValidationItem = (item) => {
  if (typeof item === 'string') {
    const text = item.replace(/^Value error,\s*/i, '').trim()
    return text.endsWith('.') ? text : `${text}.`
  }
  if (!item || typeof item !== 'object') return ''

  const label = fieldLabelFromLoc(item.loc)
  const raw = String(item.msg || item.message || '').replace(/^Value error,\s*/i, '').trim()
  if (!raw) return label ? `${label} is invalid.` : ''
  if (/field required/i.test(raw) || /is required/i.test(raw)) {
    return label ? `${label} is required.` : 'A required field is missing.'
  }
  const sentence = raw.endsWith('.') ? raw : `${raw}.`
  if (label && !raw.toLowerCase().includes(String(label).toLowerCase())) {
    return `${label}: ${sentence}`
  }
  return sentence
}

export const formatApiErrorDetail = (detail, status = 500) => {
  if (detail == null || detail === '') {
    return `Request failed (HTTP ${status}).`
  }
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const parts = [...new Set(detail.map(formatValidationItem).filter(Boolean))]
    const required = parts.filter((part) => / is required\.$/.test(part))
    const other = parts.filter((part) => !/ is required\.$/.test(part))
    if (required.length >= 3 && other.length === 0) {
      const labels = required.map((part) => part.replace(/ is required\.$/, ''))
      return `Enter the missing birth data: ${joinList(labels)}.`
    }
    if (parts.length) return parts.join(' ')
    return `Request failed (HTTP ${status}).`
  }
  if (typeof detail === 'object') {
    if (typeof detail.msg === 'string') return detail.msg
    if (typeof detail.message === 'string') return detail.message
    try {
      return JSON.stringify(detail)
    } catch {
      return `Request failed (HTTP ${status}).`
    }
  }
  return String(detail)
}

export const toUserErrorMessage = (error, fallback = 'Something went wrong.') => {
  let text = typeof error === 'string' ? error : error?.message || ''
  text = text.replace(/^Error invoking remote method '[^']+':\s*/i, '')
  text = text.replace(/^Error:\s*/i, '')
  text = text.replace(/^HTTP \d+:\s*/i, '')
  text = text.replace(/\[object Object\](?:,\s*\[object Object\])*/g, '')
  text = text.replace(/\s+/g, ' ').replace(/^[:\s]+|[:\s]+$/g, '').trim()
  return text || fallback
}
