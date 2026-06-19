import { createFileRoute } from "@tanstack/react-router"

import { PageTemplate } from "@/components/Common/PageTemplate"
import { SectionShell } from "@/components/Home/SectionShell"
import { ProfileViewSection } from "@/components/Profile/ProfileViewSection"
import { YourLinksSection } from "@/components/Profile/YourLinksSection"
import { Card } from "@/components/retroui/Card"
import { ItchLoginButton } from "@/components/Submit/ItchLoginButton"
import useCurrentUser, { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_public/profile")({
  component: ProfilePage,
  head: () => ({
    meta: [{ title: "Profile - Index of Our Own" }],
  }),
})

function ProfileLoginGate() {
  return (
    <PageTemplate
      title="Profile"
      description="Log in with your itch.io account to edit your profile."
    >
      <Card className="mx-auto flex max-w-md flex-col items-center gap-4 p-8 text-center">
        <ItchLoginButton returnTo="/profile" />
      </Card>
    </PageTemplate>
  )
}

function ProfileEditor({
  user,
}: {
  user: NonNullable<ReturnType<typeof useCurrentUser>["user"]>
}) {
  return (
    <PageTemplate title="Profile" description="Manage how you appear on io3.">
      <div className="flex flex-col gap-6">
        <SectionShell className="bg-white p-4 md:p-5">
          <ProfileViewSection user={user} />
        </SectionShell>
        <SectionShell className="bg-white p-4 md:p-5">
          <YourLinksSection
            profileLinks={user.profile_links ?? []}
            itchUsername={user.itch_username}
          />
        </SectionShell>
      </div>
    </PageTemplate>
  )
}

function ProfilePage() {
  const { user, isLoading } = useCurrentUser()

  if (!isLoggedIn()) {
    return <ProfileLoginGate />
  }

  if (isLoading || !user) {
    return (
      <PageTemplate title="Profile" description="Manage how you appear on io3.">
        <SectionShell className="bg-white p-4 md:p-5" aria-busy="true">
          {null}
        </SectionShell>
      </PageTemplate>
    )
  }

  return <ProfileEditor user={user} />
}
