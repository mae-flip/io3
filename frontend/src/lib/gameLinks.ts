import type { GamePublic } from "@/client"

export function getPrimaryLink(game: GamePublic) {
  return game.links?.find((link) => link.is_primary) ?? game.links?.[0]
}
