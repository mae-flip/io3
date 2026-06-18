const STORAGE_KEY = "io3_age_verified"

export function isAgeVerified(): boolean {
  return localStorage.getItem(STORAGE_KEY) === "true"
}

export function setAgeVerified(): void {
  localStorage.setItem(STORAGE_KEY, "true")
}

export function clearAgeVerified(): void {
  localStorage.removeItem(STORAGE_KEY)
}
