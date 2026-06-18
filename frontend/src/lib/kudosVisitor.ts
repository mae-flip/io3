const STORAGE_KEY = "io3_kudos_visitor_id"

export function getKudosVisitorId(): string {
  const existing = localStorage.getItem(STORAGE_KEY)
  if (existing) {
    return existing
  }
  const visitorId = crypto.randomUUID()
  localStorage.setItem(STORAGE_KEY, visitorId)
  return visitorId
}
