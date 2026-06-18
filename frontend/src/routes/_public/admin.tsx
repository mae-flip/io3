import { createFileRoute } from "@tanstack/react-router"

import AddGameUrl from "@/components/Admin/AddGameUrl"
import { AdminGamesTable } from "@/components/Admin/AdminGamesTable"
import { NewsletterSubscribersCard } from "@/components/Admin/NewsletterSubscribersCard"
import { ModeratorsTable } from "@/components/Admin/ModeratorsTable"
import { ItchLoginButton } from "@/components/Submit/ItchLoginButton"
import PendingGames from "@/components/Pending/PendingGames"
import { Card } from "@/components/retroui/Card"
import useCurrentUser, { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_public/admin")({
  component: AdminPage,
  head: () => ({
    meta: [{ title: "Admin - Index of Our Own" }],
  }),
})

function AdminLoginGate() {
  return (
    <Card className="mx-auto max-w-md p-8 text-center">
      <h1 className="font-head text-2xl tracking-wide uppercase">Admin</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Log in with your itch.io account to access the admin area.
      </p>
      <div className="mt-6 flex justify-center">
        <ItchLoginButton returnTo="/admin" />
      </div>
    </Card>
  )
}

function AdminAccessDenied() {
  const { user, logout } = useCurrentUser()

  return (
    <Card className="mx-auto max-w-md p-8 text-center">
      <h1 className="font-head text-2xl tracking-wide uppercase">Access denied</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        {user?.itch_username
          ? `Signed in as ${user.itch_username}, but this account does not have admin access.`
          : "This account does not have admin access."}
      </p>
      <button
        type="button"
        className="mt-6 text-sm underline text-muted-foreground hover:text-foreground"
        onClick={() => logout()}
      >
        Log out
      </button>
    </Card>
  )
}

function AdminContent() {
  const { isOwner } = useCurrentUser()

  return (
    <div className="flex flex-col gap-10">
      {isOwner && <NewsletterSubscribersCard />}

      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="font-head text-3xl tracking-wide uppercase">Admin</h1>
            <p className="text-muted-foreground">
              Add or remove itch.io game URLs from the index.
            </p>
          </div>
          <AddGameUrl />
        </div>
        <AdminGamesTable />
      </div>

      {isOwner && (
        <div className="flex flex-col gap-4">
          <div>
            <h2 className="font-head text-2xl tracking-wide uppercase">
              Moderators
            </h2>
            <p className="text-muted-foreground">
              Choose which itch.io users can access this admin page.
            </p>
          </div>
          <ModeratorsTable />
        </div>
      )}
    </div>
  )
}

function AdminPage() {
  const { user, isLoading, canAccessAdmin } = useCurrentUser()

  if (!isLoggedIn()) {
    return <AdminLoginGate />
  }

  if (isLoading) {
    return <PendingGames />
  }

  if (!user || !canAccessAdmin) {
    return <AdminAccessDenied />
  }

  return <AdminContent />
}
