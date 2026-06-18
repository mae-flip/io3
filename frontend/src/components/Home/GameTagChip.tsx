import { useNavigate } from "@tanstack/react-router"

import type { TagPublic } from "@/client"
import { tagChipClassName } from "@/lib/gameTags"
import { cn } from "@/lib/utils"

interface GameTagChipProps {
  tag: TagPublic
  size?: "sm" | "xs"
}

export function GameTagChip({ tag, size = "sm" }: GameTagChipProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    navigate({
      to: "/",
      search: (prev) => ({
        ...prev,
        search: tag.name,
        skip: 0,
      }),
    })
    document.getElementById("full-index")?.scrollIntoView({ behavior: "smooth" })
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className={cn(tagChipClassName(tag.is_genre, size), "cursor-pointer")}
    >
      {tag.name}
    </button>
  )
}
