import type { GamePublic } from "@/client"
import { formatGamePrice } from "@/lib/gamePrice"
import { cn } from "@/lib/utils"

interface GamePriceLabelProps {
  game: GamePublic
  size?: "xs" | "sm"
  className?: string
}

export function GamePriceLabel({
  game,
  size = "sm",
  className,
}: GamePriceLabelProps) {
  const label = formatGamePrice(game.price_cents, game.price_currency)
  if (!label) return null

  return (
    <span
      className={cn(
        "shrink-0 font-sans font-medium text-black",
        size === "xs" ? "text-xs" : "text-xs md:text-sm",
        className,
      )}
    >
      {label}
    </span>
  )
}
