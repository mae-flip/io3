import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

import { GamesService } from "@/client"
import { FullIndexSection } from "@/components/Home/FullIndexSection"
import type { SortOption } from "@/components/Home/SortTabs"
import { SupportCard } from "@/components/Home/SupportCard"
import { WeeklyFeaturesSection } from "@/components/Home/WeeklyFeaturesSection"
import { WelcomeSection } from "@/components/Home/WelcomeSection"

const homeSearchSchema = z.object({
  search: z.string().optional(),
  sort: z
    .enum(["latest", "title", "author", "kudos"])
    .optional()
    .default("latest"),
  skip: z.number().optional().default(0),
  platforms: z
    .array(z.enum(["web", "windows", "linux", "apple"]))
    .optional()
    .default([]),
})

export const Route = createFileRoute("/_public/")({
  component: Home,
  validateSearch: homeSearchSchema,
  head: () => ({
    meta: [{ title: "Index of our own" }],
  }),
})

function Home() {
  const {
    search = "",
    sort = "latest",
    skip = 0,
    platforms = [],
  } = Route.useSearch()

  const { data: featuredData, isLoading: featuredLoading } = useQuery({
    queryKey: ["games", "featured"],
    queryFn: () => GamesService.readFeaturedGames({ limit: 3 }),
  })

  return (
    <div className="flex flex-col gap-8 md:gap-10">
      <div className="flex flex-col gap-4 md:flex-row md:items-stretch">
        <WelcomeSection />
        <SupportCard />
      </div>
      <WeeklyFeaturesSection
        games={featuredData?.data ?? []}
        isLoading={featuredLoading}
      />
      <FullIndexSection
        search={search}
        sort={sort as SortOption}
        skip={skip}
        platforms={platforms}
      />
      <p className="text-center font-sans text-sm text-dark-grey">
        Made with love by{" "}
        <a
          href="https://maeflip.itch.io/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-black underline hover:no-underline"
        >
          MaeFlip
        </a>{" "}
        <span className="text-pink">&lt;3</span>
      </p>
    </div>
  )
}
