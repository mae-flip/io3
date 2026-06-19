import { ChevronDown } from "lucide-react"

import type { UserProfileLink } from "@/client"
import { ProfileLinkIcon } from "@/components/Profile/ProfileLinkIcon"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

function displayUrl(url: string) {
  try {
    const parsed = new URL(url)
    const path = parsed.pathname === "/" ? "" : parsed.pathname.replace(/\/$/, "")
    return `${parsed.hostname}${path}`
  } catch {
    return url
  }
}

interface AuthorProfileLinksProps {
  name: string
  profileLinks?: UserProfileLink[]
  fallbackUrl?: string | null
  className?: string
}

export function AuthorProfileLinks({
  name,
  profileLinks,
  fallbackUrl,
  className,
}: AuthorProfileLinksProps) {
  const links = profileLinks?.filter((link) => link.url) ?? []

  if (links.length > 1) {
    return (
      <DropdownMenu modal={false}>
        <DropdownMenuTrigger asChild>
          <button
            type="button"
            className={cn(
              "inline-flex shrink-0 items-center gap-0.5 font-sans text-pink hover:underline",
              className,
            )}
            aria-label={`${name} profile links`}
          >
            {name}
            <ChevronDown className="size-3.5 shrink-0" aria-hidden />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="max-w-xs">
          {links.map((link) => (
            <DropdownMenuItem key={link.url} asChild>
              <a
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex min-w-0 items-center gap-2"
              >
                <ProfileLinkIcon url={link.url} className="text-dark-grey" />
                <span className="truncate">{displayUrl(link.url)}</span>
              </a>
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    )
  }

  const linkUrl = links[0]?.url ?? fallbackUrl ?? null
  if (linkUrl) {
    return (
      <a
        href={linkUrl}
        target="_blank"
        rel="noopener noreferrer"
        className={cn(
          "shrink-0 font-sans text-pink hover:underline",
          className,
        )}
      >
        {name}
      </a>
    )
  }

  return (
    <span className={cn("shrink-0 font-sans text-pink", className)}>{name}</span>
  )
}
