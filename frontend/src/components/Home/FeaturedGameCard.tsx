import type { GamePublic } from "@/client"
import { Card } from "@/components/retroui/Card"
import { KudosButton } from "@/components/Home/KudosButton"
import { GamePriceLabel } from "@/components/Home/GamePriceLabel"
import { GameTagChip } from "@/components/Home/GameTagChip"
import { PlatformChip } from "@/components/Home/PlatformChip"
import { getPrimaryLink } from "@/lib/gameLinks"
import { orderFeaturedTags } from "@/lib/gameTags"
import { orderPlatforms } from "@/lib/platformTags"
import { cn } from "@/lib/utils"

interface FeaturedGameCardProps {
  game: GamePublic
  className?: string
}

export function FeaturedGameCard({ game, className }: FeaturedGameCardProps) {
  const primaryLink = getPrimaryLink(game)
  const hoverText = game.summary?.trim()

  return (
    <Card className={cn("group flex flex-col overflow-hidden bg-white retro-shadow-sm", className)}>
      <div className="border-b-2 border-black p-3">
        <h3 className="font-head-sm text-base leading-tight">{game.title}</h3>
      </div>

      <a
        href={primaryLink?.url}
        target="_blank"
        rel="noopener noreferrer"
        className="block"
      >
        <div className="relative aspect-thumbnail bg-light-grey">
          {game.cover_image_url ? (
            <img
              src={game.cover_image_url}
              alt={game.title ?? ""}
              className="h-full w-full object-cover"
            />
          ) : null}
          {hoverText ? (
            <div className="pointer-events-none absolute inset-0 flex flex-col justify-end opacity-0 transition-opacity group-hover:opacity-100">
              <div className="min-h-0 flex-1 bg-gradient-to-b from-transparent to-black/80" />
              <div className="bg-black/80 p-2">
                <p className="line-clamp-4 font-sans text-xs leading-snug text-white md:text-sm">
                  {hoverText}
                </p>
              </div>
            </div>
          ) : null}
        </div>
      </a>

      <div className="flex flex-1 flex-col gap-3 p-3">
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs md:text-sm">
            <span className="font-sans">
            Author:{" "}
            {game.author_url ? (
              <a
                href={game.author_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-pink hover:underline"
              >
                {game.author_name ?? "Unknown"}
              </a>
            ) : (
              <span className="text-pink">{game.author_name ?? "Unknown"}</span>
            )}
          </span>
          <KudosButton game={game} />
        </div>

        {game.summary && (
          <p className="line-clamp-3 font-sans text-xs leading-relaxed text-black md:text-sm">
            {game.summary}
          </p>
        )}

        {game.platforms && game.platforms.length > 0 ? (
          <div className="flex flex-wrap gap-1.5">
            {orderPlatforms(game.platforms).map((platform) => (
              <PlatformChip key={platform.platform} platform={platform} />
            ))}
          </div>
        ) : null}

        <div className="mt-auto flex items-end justify-between gap-2">
          <div className="flex flex-wrap gap-1.5">
            {orderFeaturedTags(game.tags ?? []).map((tag) => (
              <GameTagChip key={tag.id} tag={tag} />
            ))}
          </div>
          <GamePriceLabel game={game} />
        </div>
      </div>
    </Card>
  )
}
