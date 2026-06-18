import type * as React from "react"

import { cn } from "@/lib/utils"

function Card({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "border-2 border-black bg-card text-card-foreground retro-shadow",
        className,
      )}
      {...props}
    />
  )
}

export { Card }
