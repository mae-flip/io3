import { useQuery } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { GamesService } from "@/client"
import { CompactGameCard } from "@/components/Home/CompactGameCard"
import { GameGridSkeleton } from "@/components/Home/GameGridSkeleton"
import { PlatformFilters } from "@/components/Home/PlatformFilters"
import { SectionShell, SectionTitle } from "@/components/Home/SectionShell"
import { type SortOption, SortTabs } from "@/components/Home/SortTabs"
import { Button } from "@/components/retroui/Button"
import type { IndexPlatformFilter } from "@/lib/platformTags"

const PAGE_SIZE = 20

interface FullIndexSectionProps {
  search?: string
  sort: SortOption
  skip: number
  platforms: IndexPlatformFilter[]
}

export function FullIndexSection({
  search,
  sort,
  skip,
  platforms,
}: FullIndexSectionProps) {
  const navigate = useNavigate({ from: "/" })

  const { data, isLoading } = useQuery({
    queryKey: ["games", "index", search, sort, skip, platforms],
    queryFn: () =>
      GamesService.readGames({
        skip,
        limit: PAGE_SIZE,
        search: search || undefined,
        sort,
        platforms: platforms.length > 0 ? platforms : undefined,
      }),
  })

  const games = data?.data ?? []
  const total = data?.count ?? 0
  const hasMore = skip + PAGE_SIZE < total
  const hasPrev = skip > 0

  const updateSearch = (updates: {
    sort?: SortOption
    skip?: number
    platforms?: IndexPlatformFilter[]
  }) => {
    navigate({
      search: (prev) => ({
        ...prev,
        sort: updates.sort ?? sort,
        skip: updates.skip ?? skip,
        platforms: updates.platforms ?? platforms,
      }),
    })
  }

  return (
    <SectionShell id="full-index" className="bg-white">
      <div className="border-b-2 border-black px-4 py-4 md:px-6">
        <SectionTitle>Full Index</SectionTitle>
      </div>

      <SortTabs
        value={sort}
        onChange={(next) => updateSearch({ sort: next, skip: 0 })}
      />
      <PlatformFilters
        value={platforms}
        onChange={(next) => updateSearch({ platforms: next, skip: 0 })}
      />

      <div className="p-4 md:p-6">
        {isLoading ? (
          <GameGridSkeleton />
        ) : games.length === 0 ? (
          <p className="font-sans text-dark-grey">
            {search || platforms.length > 0
              ? "No games match your filters."
              : "No games indexed yet."}
          </p>
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {games.map((game) => (
              <CompactGameCard key={game.id} game={game} />
            ))}
          </div>
        )}

        {(hasPrev || hasMore) && (
          <div className="mt-6 flex justify-center gap-3">
            {hasPrev && (
              <Button
                type="button"
                variant="default"
                size="sm"
                onClick={() =>
                  updateSearch({ skip: Math.max(0, skip - PAGE_SIZE) })
                }
              >
                Previous
              </Button>
            )}
            {hasMore && (
              <Button
                type="button"
                variant="default"
                size="sm"
                onClick={() => updateSearch({ skip: skip + PAGE_SIZE })}
              >
                Next
              </Button>
            )}
          </div>
        )}
      </div>
    </SectionShell>
  )
}
