import type { CSSProperties, ReactNode } from "react"

import {
  HEADER_HEIGHT,
  SiteFrameRail,
  siteFrameRailWidth,
} from "@/components/Common/SiteFrameRail"
import { cn } from "@/lib/utils"

interface SiteFrameProps {
  children: ReactNode
  className?: string
}

export function SiteFrame({ children, className }: SiteFrameProps) {
  return (
    <div
      className={cn(
        "min-h-svh bg-faded-plastic p-2 [--site-frame-padding:0.5rem] md:p-3 md:[--site-frame-padding:0.75rem]",
        className,
      )}
    >
      <div
        className="relative min-h-[calc(100svh-1rem)] md:min-h-[calc(100svh-1.5rem)]"
        style={
          {
            "--site-rail-width": `${siteFrameRailWidth}px`,
            "--site-header-height": `${HEADER_HEIGHT}px`,
          } as CSSProperties
        }
      >
        <SiteFrameRail />
        <div className="relative z-10 flex min-h-[inherit] flex-col">
          {children}
        </div>
      </div>
    </div>
  )
}
