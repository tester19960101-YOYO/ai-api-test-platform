export function stringifyJson(value: unknown): string {
  if (value === undefined || value === null) {
    return ''
  }
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

export function parseJsonObject(text: string, fallback: Record<string, unknown> | null = null) {
  const trimmed = text.trim()
  if (!trimmed) {
    return fallback
  }
  const parsed = JSON.parse(trimmed)
  if (typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error('JSON 必须是对象')
  }
  return parsed as Record<string, unknown>
}

export function parseJsonArray(text: string, fallback: unknown[] | null = null) {
  const trimmed = text.trim()
  if (!trimmed) {
    return fallback
  }
  const parsed = JSON.parse(trimmed)
  if (!Array.isArray(parsed)) {
    throw new Error('JSON 必须是数组')
  }
  return parsed
}
