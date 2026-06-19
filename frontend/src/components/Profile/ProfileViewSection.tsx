import type { UserPublic } from "@/client"
import { ItchManagedField } from "@/components/Profile/ItchManagedField"
import { SectionTitle } from "@/components/Home/SectionShell"

interface ProfileViewSectionProps {
  user: UserPublic
}

function formatMemberSince(createdAt: string | null | undefined) {
  if (!createdAt) return "—"
  return new Date(createdAt).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  })
}

function io3Roles(user: UserPublic) {
  const roles: string[] = []
  if (user.is_owner) roles.push("Site owner")
  if (user.is_moderator) roles.push("Moderator")
  return roles
}

export function ProfileViewSection({ user }: ProfileViewSectionProps) {
  const username = user.itch_username
  const displayName = user.display_name || username || "—"
  const roles = io3Roles(user)

  return (
    <section className="flex flex-col gap-4">
      <SectionTitle className="text-xl md:text-2xl">Your profile</SectionTitle>

      <dl className="grid gap-4 sm:grid-cols-2">
        <ItchManagedField label="Display name">{displayName}</ItchManagedField>

        <ItchManagedField label="Itch username">
          {username ? (
            <a
              href="https://itch.io/user/settings"
              target="_blank"
              rel="noopener noreferrer"
              className="text-black underline hover:no-underline"
            >
              {username}
            </a>
          ) : (
            "—"
          )}
        </ItchManagedField>

        <div className="flex flex-col gap-1">
          <dt className="font-sans text-xs uppercase tracking-wide text-dark-grey">
            Member since
          </dt>
          <dd className="font-sans text-sm md:text-base">
            {formatMemberSince(user.created_at)}
          </dd>
        </div>

        {roles.length > 0 ? (
          <div className="flex flex-col gap-1">
            <dt className="font-sans text-xs uppercase tracking-wide text-dark-grey">
              io3 roles
            </dt>
            <dd className="font-sans text-sm md:text-base">{roles.join(", ")}</dd>
          </div>
        ) : null}
      </dl>
    </section>
  )
}
