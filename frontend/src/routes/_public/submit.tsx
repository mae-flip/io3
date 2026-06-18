import { createFileRoute, Outlet, useRouterState } from "@tanstack/react-router"

import { ItchGamePicker } from "@/components/Submit/ItchGamePicker"
import { ItchLoginButton } from "@/components/Submit/ItchLoginButton"
import { Card } from "@/components/retroui/Card"
import { useItchSubmit } from "@/hooks/useItchSubmit"

export const Route = createFileRoute("/_public/submit")({
  component: SubmitRoute,
  head: () => ({
    meta: [{ title: "Submit to io3" }],
  }),
})

function SubmitRoute() {
  const pathname = useRouterState({ select: (s) => s.location.pathname })
  if (pathname.endsWith("/callback")) {
    return <Outlet />
  }
  return <SubmitPage />
}

function SubmitPage() {
  const { isSubmitSessionReady } = useItchSubmit()

  if (isSubmitSessionReady) {
    return <ItchGamePicker />
  }

  return (
    <div className="mx-auto flex max-w-xl flex-col gap-6">
      <div>
        <h1 className="font-head text-3xl uppercase">Submit to io3</h1>
        <p className="mt-2 text-dark-grey">
          Log in with your itch.io account to submit games you develop. Only
          games that no longer appear in itch.io search (de-listed) can be
          indexed here.
        </p>
      </div>

      <Card className="flex flex-col items-center gap-4 p-8 text-center">
        <p className="text-sm text-dark-grey">
          You&apos;ll be redirected to itch.io to approve access, then return
          here to pick which games to submit.
        </p>
        <ItchLoginButton />
      </Card>
    </div>
  )
}
