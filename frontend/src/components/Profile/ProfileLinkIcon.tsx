import { profileLinkIconForUrl } from "@/lib/profileLinkIcons"
import { cn } from "@/lib/utils"

interface ProfileLinkIconProps {
  url: string
  className?: string
}

export function ProfileLinkIcon({ url, className }: ProfileLinkIconProps) {
  const Icon = profileLinkIconForUrl(url)

  return (
    <Icon
      className={cn("size-4 shrink-0", className)}
      aria-hidden
    />
  )
}
