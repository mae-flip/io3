export function formatGamePrice(
  priceCents: number | null | undefined,
  currency: string | null | undefined,
): string | null {
  if (priceCents == null) return null
  if (priceCents === 0) return "Free"

  const amount = priceCents / 100
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency ?? "USD",
  }).format(amount)
}
