import { createFileRoute, Outlet, useRouterState } from "@tanstack/react-router"

import { PublicNav } from "@/components/Common/PublicNav"
import { SiteFrame } from "@/components/Common/SiteFrame"

export const Route = createFileRoute("/_public")({
  component: PublicLayout,
})

function PublicLayout() {
  const pathname = useRouterState({ select: (s) => s.location.pathname })
  const showSearch = pathname === "/"

  return (
    <SiteFrame>
      <PublicNav showSearch={showSearch} />
      <main className="flex-1 md:pr-[var(--site-rail-width)]">
        <div className="mx-auto max-w-7xl px-4 py-6 md:px-8 md:py-8">
          <Outlet />
        </div>
      </main>
    </SiteFrame>
  )
}
