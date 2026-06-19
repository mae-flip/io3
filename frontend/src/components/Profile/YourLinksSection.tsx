import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus, Trash2 } from "lucide-react"
import { useEffect, useMemo, useState } from "react"

import { type UserProfileLink, UsersService } from "@/client"
import { ItchManagedField } from "@/components/Profile/ItchManagedField"
import { ProfileLinkIcon } from "@/components/Profile/ProfileLinkIcon"
import { SectionTitle } from "@/components/Home/SectionShell"
import { Button } from "@/components/retroui/Button"
import { Input } from "@/components/retroui/Input"
import useCustomToast from "@/hooks/useCustomToast"
import { cn } from "@/lib/utils"
import { handleError } from "@/utils"

const MAX_CUSTOM_LINKS = 7

type EditableProfileLink = {
  label: string
  url: string
}

interface YourLinksSectionProps {
  profileLinks: UserProfileLink[]
  itchUsername?: string | null
}

function linksEqual(a: EditableProfileLink[], b: EditableProfileLink[]) {
  return JSON.stringify(a) === JSON.stringify(b)
}

function toCustomEditableLinks(links: UserProfileLink[]): EditableProfileLink[] {
  return links
    .filter((link) => !link.managed_by_itch)
    .map((link) => ({
      label: link.label,
      url: link.url,
    }))
}

function ItchProfileLinkRow({ username }: { username: string }) {
  const profileUrl = `https://${username}.itch.io`

  return (
    <li className="flex gap-3 border-2 border-black/10 bg-faded-plastic/40 p-3">
      <ProfileLinkIcon url={profileUrl} className="mt-1 shrink-0 text-dark-grey" />
      <div className="grid min-w-0 flex-1 gap-3 sm:grid-cols-2 sm:items-end">
        <ItchManagedField label="Label">itch.io</ItchManagedField>
        <ItchManagedField label="URL">
          <a
            href={profileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-black underline hover:no-underline"
          >
            {profileUrl}
          </a>
        </ItchManagedField>
      </div>
    </li>
  )
}

export function YourLinksSection({
  profileLinks,
  itchUsername,
}: YourLinksSectionProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const savedCustomLinks = useMemo(
    () => toCustomEditableLinks(profileLinks),
    [profileLinks],
  )
  const [links, setLinks] = useState<EditableProfileLink[]>(() => savedCustomLinks)

  useEffect(() => {
    setLinks(savedCustomLinks)
  }, [savedCustomLinks])

  const isDirty = !linksEqual(links, savedCustomLinks)

  const saveMutation = useMutation({
    mutationFn: () =>
      UsersService.updateUserProfileLinks({
        requestBody: {
          links: links
            .map((link) => ({
              label: link.label.trim(),
              url: link.url.trim(),
            }))
            .filter((link) => link.label && link.url),
        },
      }),
    onSuccess: (data) => {
      queryClient.setQueryData(["currentUser"], data)
      showSuccessToast("Profile links saved")
    },
    onError: handleError.bind(showErrorToast),
  })

  const addLink = () => {
    if (links.length >= MAX_CUSTOM_LINKS) return
    setLinks((current) => [...current, { label: "", url: "" }])
  }

  const updateLink = (
    index: number,
    field: keyof EditableProfileLink,
    value: string,
  ) => {
    setLinks((current) =>
      current.map((link, linkIndex) =>
        linkIndex === index ? { ...link, [field]: value } : link,
      ),
    )
  }

  const removeLink = (index: number) => {
    setLinks((current) => current.filter((_, linkIndex) => linkIndex !== index))
  }

  return (
    <section className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <SectionTitle className="text-xl md:text-2xl">Your links</SectionTitle>
        <p className="font-sans text-sm leading-snug text-dark-grey md:text-base">
          Customize the links that appear when someone selects your profile name
          on io3.
        </p>
      </div>

      <ul className="flex flex-col gap-3">
        {itchUsername ? <ItchProfileLinkRow username={itchUsername} /> : null}

        {links.map((link, index) => (
          <li
            key={index}
            className="flex gap-3 border-2 border-black/10 bg-faded-plastic/40 p-3"
          >
            <ProfileLinkIcon
              url={link.url}
              className="mt-1 shrink-0 text-dark-grey"
            />
            <div className="grid min-w-0 flex-1 gap-3 sm:grid-cols-[minmax(0,10rem)_minmax(0,1fr)_auto] sm:items-end">
            <div className="flex flex-col gap-1">
              <label
                htmlFor={`profile-link-label-${index}`}
                className="font-sans text-xs uppercase tracking-wide text-dark-grey"
              >
                Label
              </label>
              <Input
                id={`profile-link-label-${index}`}
                value={link.label}
                placeholder="Ko-fi"
                maxLength={64}
                onChange={(event) =>
                  updateLink(index, "label", event.target.value)
                }
              />
            </div>
            <div className="flex flex-col gap-1">
              <label
                htmlFor={`profile-link-url-${index}`}
                className="font-sans text-xs uppercase tracking-wide text-dark-grey"
              >
                URL
              </label>
              <Input
                id={`profile-link-url-${index}`}
                type="url"
                value={link.url}
                placeholder="https://ko-fi.com/you"
                onChange={(event) =>
                  updateLink(index, "url", event.target.value)
                }
              />
            </div>
            <Button
              type="button"
              variant="default"
              size="sm"
              className="w-full font-head-sm uppercase tracking-wide sm:w-auto"
              onClick={() => removeLink(index)}
              aria-label={`Remove link ${index + 1}`}
            >
              <Trash2 className="size-4" aria-hidden />
              Remove
            </Button>
            </div>
          </li>
        ))}
      </ul>

      {links.length === 0 && itchUsername ? (
        <p className="font-sans text-sm text-dark-grey">
          Add optional links to show alongside your itch.io profile.
        </p>
      ) : null}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <Button
          type="button"
          variant="default"
          size="md"
          className={cn("font-head-sm uppercase tracking-wide")}
          onClick={addLink}
          disabled={links.length >= MAX_CUSTOM_LINKS}
        >
          <Plus className="size-4" aria-hidden />
          Add link
        </Button>
        <Button
          type="button"
          variant="pink"
          size="md"
          className="font-head-sm uppercase tracking-wide sm:ml-auto"
          disabled={!isDirty || saveMutation.isPending}
          onClick={() => saveMutation.mutate()}
        >
          {saveMutation.isPending ? "Saving…" : "Save links"}
        </Button>
      </div>
    </section>
  )
}
