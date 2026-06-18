import type { GamePublic } from "@/client"

import { PixelIcon } from "@/components/Common/PixelIcon"
import { FeaturedGameCard } from "@/components/Home/FeaturedGameCard"
import { GameGridSkeleton } from "@/components/Home/GameGridSkeleton"
import { NewsletterSubscribeForm } from "@/components/Home/NewsletterSubscribeForm"
import { SectionShell, SectionTitle } from "@/components/Home/SectionShell"

interface WeeklyFeaturesSectionProps {
  games: GamePublic[]
  isLoading?: boolean
}

export function WeeklyFeaturesSection({
  games,
  isLoading,
}: WeeklyFeaturesSectionProps) {
  return (
    <SectionShell id="weekly-features" className="bg-pink p-4 md:p-6">
      <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <PixelIcon name="heart" className="text-white" size={28} />
          <SectionTitle
            className="text-white"
            style={{ textShadow: "2px 2px 0 #000" }}
          >
            Weekly Features
          </SectionTitle>
        </div>
        <a
          href="#full-index"
          className="font-sans text-sm text-pink-light hover:underline"
        >
          Browse previously featured games &gt;
        </a>
      </div>

      {isLoading ? (
        <GameGridSkeleton count={3} className="md:grid-cols-3" />
      ) : games.length === 0 ? (
        <p className="font-sans text-white">No featured games yet.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          {games.map((game) => (
            <FeaturedGameCard key={game.id} game={game} />
          ))}
        </div>
      )}

      <NewsletterSubscribeForm />
    </SectionShell>
  )
}
