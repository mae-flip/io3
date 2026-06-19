import type { GamePublic } from "@/client"
import { GamePriceLabel } from "@/components/Home/GamePriceLabel"
import { GameTagChip } from "@/components/Home/GameTagChip"
import { KudosButton } from "@/components/Home/KudosButton"
import { PlatformChip } from "@/components/Home/PlatformChip"
import { AuthorProfileLinks } from "@/components/Profile/AuthorProfileLinks"
import { Card } from "@/components/retroui/Card"
import { profileLinksForDisplayedAuthor } from "@/lib/authorProfileLinks"
import { getPrimaryLink } from "@/lib/gameLinks"
import { formatGamePrice } from "@/lib/gamePrice"
import { orderDisplayTags } from "@/lib/gameTags"
import { orderPlatforms } from "@/lib/platformTags"
import { cn } from "@/lib/utils"

interface CompactGameCardProps {
  game: GamePublic
  className?: string
}

export function CompactGameCard({ game, className }: CompactGameCardProps) {
  const primaryLink = getPrimaryLink(game)
  const hoverText = game.summary?.trim()
  const tags = orderDisplayTags(game.tags ?? [])
  const platforms = orderPlatforms(game.platforms ?? [])

  const authorLabel = game.author_name ?? "Unknown"
  const authorElement = (
    <AuthorProfileLinks
      name={authorLabel}
      profileLinks={profileLinksForDisplayedAuthor(game)}
      fallbackUrl={game.author_url}
      className="text-xs"
    />
  )

  const header = (
    <div className="border-b-2 border-black p-2">
      <div className="flex items-start justify-between gap-2">
        {primaryLink ? (
          <a
            href={primaryLink.url}
            target="_blank"
            rel="noopener noreferrer"
            className="min-w-0 flex-1"
          >
            <h3 className="font-head-sm text-sm leading-tight line-clamp-2">
              {game.title}
            </h3>
          </a>
        ) : (
          <h3 className="min-w-0 flex-1 font-head-sm text-sm leading-tight line-clamp-2">
            {game.title}
          </h3>
        )}
        {authorElement}
      </div>
    </div>
  )

  const thumbnail = (
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
            <p className="line-clamp-4 font-sans text-xs leading-snug text-white">
              {hoverText}
            </p>
          </div>
        </div>
      ) : null}
    </div>
  )

  const priceLabel = formatGamePrice(game.price_cents, game.price_currency)

  return (
    <Card
      className={cn(
        "group flex h-full flex-col overflow-hidden bg-white retro-shadow-sm",
        className,
      )}
    >
      {header}
      {primaryLink ? (
        <a
          href={primaryLink.url}
          target="_blank"
          rel="noopener noreferrer"
          className="block"
        >
          {thumbnail}
        </a>
      ) : (
        thumbnail
      )}

      <div className="flex min-h-0 flex-1 flex-col gap-1 border-t-2 border-black p-2">
        <div className="flex items-center justify-between gap-2">
          <div className="flex min-w-0 flex-wrap gap-1">
            {platforms.map((platform) => (
              <PlatformChip
                key={platform.platform}
                platform={platform}
                size="xs"
              />
            ))}
          </div>
          <KudosButton game={game} size="xs" showLabel={false} />
        </div>

        {tags.length > 0 ? (
          <div className="flex w-full flex-wrap gap-1">
            {tags.map((tag) => (
              <GameTagChip key={tag.id} tag={tag} size="xs" />
            ))}
          </div>
        ) : null}

        {priceLabel ? (
          <GamePriceLabel game={game} size="xs" className="mt-auto self-end" />
        ) : null}
      </div>
    </Card>
  )
}
