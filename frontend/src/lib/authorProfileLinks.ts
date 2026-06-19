import type { GamePublic, UserProfileLink } from "@/client"

function normalizeUrl(url: string) {
  return url.replace(/\/$/, "").toLowerCase()
}

export function submitterItchProfileUrl(username: string) {
  return `https://${username}.itch.io`
}

export function authorMatchesSubmitter(game: GamePublic): boolean {
  const username = game.submitter_itch_username
  if (!username) return false

  const submitterProfile = submitterItchProfileUrl(username)
  if (game.author_url) {
    return normalizeUrl(game.author_url) === normalizeUrl(submitterProfile)
  }

  if (game.author_name) {
    return game.author_name.toLowerCase() === username.toLowerCase()
  }

  return false
}

export function profileLinksForDisplayedAuthor(
  game: GamePublic,
): UserProfileLink[] | undefined {
  if (!authorMatchesSubmitter(game)) return undefined
  return game.submitter_profile_links
}
