import type { TagPublic } from "@/client"

export function orderFeaturedTags(tags: TagPublic[]): TagPublic[] {
  const genres = tags.filter((tag) => tag.is_genre)
  const rest = tags.filter((tag) => !tag.is_genre)
  return [...genres.slice(0, 2), ...rest].slice(0, 9)
}

export function orderDisplayTags(tags: TagPublic[]): TagPublic[] {
  const genres = tags.filter((tag) => tag.is_genre)
  const rest = tags.filter((tag) => !tag.is_genre)
  return [...genres, ...rest]
}

export function tagChipClassName(isGenre?: boolean, size: "sm" | "xs" = "sm") {
  const text = size === "xs" ? "text-[10px] leading-tight" : "text-xs"
  const padding = size === "xs" ? "px-1.5" : "px-2"
  if (isGenre) {
    return `rounded-sm bg-pink ${padding} py-0.5 font-sans ${text} text-white hover:opacity-90`
  }
  return `rounded-sm bg-light-grey ${padding} py-0.5 font-sans ${text} text-dark-grey hover:underline`
}
