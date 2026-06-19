import { useMutation, useQueryClient } from "@tanstack/react-query"
import { FaHeart, FaRegHeart } from "react-icons/fa6"

import { ApiError, GamesService, type GamePublic } from "@/client"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

interface KudosButtonProps {
  game: GamePublic
  size?: "xs" | "sm"
  showLabel?: boolean
  className?: string
}

export function KudosButton({
  game,
  size = "sm",
  showLabel = true,
  className,
}: KudosButtonProps) {
  const queryClient = useQueryClient()
  const hasKudos = Boolean(game.has_kudos)

  const mutation = useMutation({
    mutationFn: () => GamesService.addKudos({ slug: game.slug }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["games"] })
    },
  })

  const kudosGiven = hasKudos || mutation.isSuccess
  const HeartIcon = kudosGiven ? FaHeart : FaRegHeart
  const tooltipText = kudosGiven ? "You left kudos" : "+ add kudos"

  const button = (
    <button
      type="button"
      disabled={hasKudos || mutation.isPending}
      onClick={(event) => {
        event.preventDefault()
        event.stopPropagation()
        mutation.mutate()
      }}
      className={cn(
        "inline-flex shrink-0 items-center gap-1 whitespace-nowrap font-sans text-dark-grey transition-colors",
        size === "xs" ? "text-[10px]" : "text-xs",
        kudosGiven ? "cursor-default text-pink" : "hover:text-pink",
        className,
      )}
      aria-label={kudosGiven ? "Kudos given" : "Leave kudos"}
      title={showLabel ? (kudosGiven ? "You left kudos" : "Leave kudos") : undefined}
    >
      {showLabel && !kudosGiven ? <span>+ add kudos</span> : null}
      <HeartIcon
        className={cn(
          "shrink-0",
          size === "xs" ? "h-3.5 w-3.5" : "h-4 w-4",
          kudosGiven ? "text-pink" : "text-current",
        )}
        aria-hidden
      />
      <span>{game.kudos_count ?? 0}</span>
      {mutation.isError && mutation.error instanceof ApiError && (
        <span className="sr-only">{String(mutation.error.body)}</span>
      )}
    </button>
  )

  if (!showLabel) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>{button}</TooltipTrigger>
        <TooltipContent side="bottom">{tooltipText}</TooltipContent>
      </Tooltip>
    )
  }

  return button
}
