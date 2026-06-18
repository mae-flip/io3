import { createFileRoute, Outlet } from "@tanstack/react-router"

import { PublicNav } from "@/components/Common/PublicNav"
import { SiteFrame } from "@/components/Common/SiteFrame"

export const Route = createFileRoute("/_public")({
  component: PublicLayout,
})

function PublicLayout() {
  return (
    <SiteFrame>
      <PublicNav />
      <main className="flex-1 md:pr-[var(--site-rail-width)]">
        <div className="mx-auto max-w-7xl px-4 py-6 md:px-8 md:py-8">
          <Outlet />
        </div>
      </main>
    </SiteFrame>
  )
}
