import type * as React from "react"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      className={cn(
        "flex h-11 w-full border-2 border-black bg-white px-3 py-2 font-sans text-sm shadow-none outline-none placeholder:text-dark-grey focus-visible:ring-2 focus-visible:ring-black",
        className,
      )}
      {...props}
    />
  )
}

export { Input }
