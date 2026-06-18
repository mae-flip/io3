import type { PlatformPublic } from "@/client"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import {
  platformChipClassName,
  platformIcon,
} from "@/lib/platformTags"
import { cn } from "@/lib/utils"

interface PlatformChipProps {
  platform: PlatformPublic
  size?: "sm" | "xs"
  className?: string
}

export function PlatformChip({
  platform,
  size = "sm",
  className,
}: PlatformChipProps) {
  const styles = platformChipClassName(size)
  const Icon = platformIcon(platform.platform)

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span
          aria-label={platform.name}
          className={cn(styles.box, className)}
        >
          <Icon className={styles.icon} aria-hidden />
        </span>
      </TooltipTrigger>
      <TooltipContent side="bottom">{platform.name}</TooltipContent>
    </Tooltip>
  )
}
