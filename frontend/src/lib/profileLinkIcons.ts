import type { IconType } from "react-icons"
import {
  FaArrowUpRightFromSquare,
  FaBluesky,
  FaDeviantart,
  FaIdBadge,
  FaInstagram,
  FaItchIo,
  FaPatreon,
  FaTumblr,
  FaTwitch,
  FaXTwitter,
} from "react-icons/fa6"
import { SiKofi } from "react-icons/si"

export type ProfileLinkIconKey =
  | "deviantart"
  | "x"
  | "bluesky"
  | "tumblr"
  | "kofi"
  | "patreon"
  | "carrd"
  | "itch"
  | "twitch"
  | "instagram"
  | "external"

const PROFILE_LINK_ICONS: Record<ProfileLinkIconKey, IconType> = {
  deviantart: FaDeviantart,
  x: FaXTwitter,
  bluesky: FaBluesky,
  tumblr: FaTumblr,
  kofi: SiKofi,
  patreon: FaPatreon,
  carrd: FaIdBadge,
  itch: FaItchIo,
  twitch: FaTwitch,
  instagram: FaInstagram,
  external: FaArrowUpRightFromSquare,
}

type DomainMatcher = {
  key: ProfileLinkIconKey
  matches: (host: string) => boolean
}

const DOMAIN_MATCHERS: DomainMatcher[] = [
  {
    key: "deviantart",
    matches: (host) =>
      host === "deviantart.com" || host.endsWith(".deviantart.com"),
  },
  {
    key: "x",
    matches: (host) =>
      host === "x.com" ||
      host === "twitter.com" ||
      host.endsWith(".twitter.com"),
  },
  {
    key: "bluesky",
    matches: (host) =>
      host === "bsky.app" ||
      host.endsWith(".bsky.app") ||
      host === "bsky.social" ||
      host.endsWith(".bsky.social"),
  },
  {
    key: "tumblr",
    matches: (host) => host === "tumblr.com" || host.endsWith(".tumblr.com"),
  },
  {
    key: "kofi",
    matches: (host) => host === "ko-fi.com" || host.endsWith(".ko-fi.com"),
  },
  {
    key: "patreon",
    matches: (host) => host === "patreon.com" || host.endsWith(".patreon.com"),
  },
  {
    key: "carrd",
    matches: (host) =>
      host === "carrd.co" ||
      host.endsWith(".carrd.co") ||
      host === "carrd.com" ||
      host.endsWith(".carrd.com"),
  },
  {
    key: "itch",
    matches: (host) => host === "itch.io" || host.endsWith(".itch.io"),
  },
  {
    key: "twitch",
    matches: (host) => host === "twitch.tv" || host.endsWith(".twitch.tv"),
  },
  {
    key: "instagram",
    matches: (host) =>
      host === "instagram.com" || host.endsWith(".instagram.com"),
  },
]

function normalizeHostname(url: string): string | null {
  const trimmed = url.trim()
  if (!trimmed) return null

  try {
    const parsed = new URL(
      trimmed.includes("://") ? trimmed : `https://${trimmed}`,
    )
    return parsed.hostname.toLowerCase().replace(/^www\./, "")
  } catch {
    return null
  }
}

export function profileLinkIconKeyForUrl(url: string): ProfileLinkIconKey {
  const host = normalizeHostname(url)
  if (!host) return "external"

  for (const matcher of DOMAIN_MATCHERS) {
    if (matcher.matches(host)) return matcher.key
  }

  return "external"
}

export function profileLinkIconForUrl(url: string): IconType {
  return PROFILE_LINK_ICONS[profileLinkIconKeyForUrl(url)]
}
