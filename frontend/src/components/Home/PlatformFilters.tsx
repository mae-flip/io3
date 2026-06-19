import { Checkbox } from "@/components/ui/checkbox"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import type { IndexPlatformFilter } from "@/lib/platformTags"
import { INDEX_PLATFORM_FILTERS, platformIcon } from "@/lib/platformTags"
import { cn } from "@/lib/utils"

interface PlatformFiltersProps {
  value: IndexPlatformFilter[]
  onChange: (value: IndexPlatformFilter[]) => void
}

export function PlatformFilters({ value, onChange }: PlatformFiltersProps) {
  const toggle = (platform: IndexPlatformFilter) => {
    if (value.includes(platform)) {
      onChange(value.filter((item) => item !== platform))
      return
    }
    onChange([...value, platform])
  }

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 border-b-2 border-black bg-white px-4 py-2">
      {INDEX_PLATFORM_FILTERS.map(({ platform, label }) => {
        const Icon = platformIcon(platform)
        const checked = value.includes(platform)

        return (
          <label
            key={platform}
            className={cn(
              "flex cursor-pointer items-center gap-1.5",
              checked ? "text-black" : "text-dark-grey",
            )}
            aria-label={label}
          >
            <Checkbox
              checked={checked}
              onCheckedChange={() => toggle(platform)}
              className="size-3.5 border border-black bg-white data-[state=checked]:bg-pink data-[state=checked]:text-white data-[state=checked]:border-black"
            />
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="inline-flex">
                  <Icon className="h-3 w-3" aria-hidden />
                </span>
              </TooltipTrigger>
              <TooltipContent side="bottom">{label}</TooltipContent>
            </Tooltip>
          </label>
        )
      })}
    </div>
  )
}
