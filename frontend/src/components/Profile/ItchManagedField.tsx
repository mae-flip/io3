import type { ReactNode } from "react"

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

interface ItchManagedFieldProps {
  label: string
  children: ReactNode
  className?: string
}

export function ItchManagedField({
  label,
  children,
  className,
}: ItchManagedFieldProps) {
  return (
    <div className={cn("flex flex-col gap-1", className)}>
      <dt className="font-sans text-xs uppercase tracking-wide text-dark-grey">
        {label}
      </dt>
      <dd className="font-sans text-sm md:text-base">
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="inline-flex cursor-help border-b border-dotted border-dark-grey/40">
              {children}
            </span>
          </TooltipTrigger>
          <TooltipContent side="bottom">Managed by itch.io</TooltipContent>
        </Tooltip>
      </dd>
    </div>
  )
}
