import type { ComponentProps, ReactNode } from "react"

import { cn } from "@/lib/utils"

interface SectionShellProps {
  id?: string
  className?: string
  children: ReactNode
}

export function SectionShell({ id, className, children }: SectionShellProps) {
  return (
    <section
      id={id}
      className={cn("border-2 border-black retro-shadow", className)}
    >
      {children}
    </section>
  )
}

export function SectionTitle({
  className,
  children,
  ...props
}: ComponentProps<"h2">) {
  return (
    <h2
      className={cn(
        "font-head-md text-2xl uppercase tracking-wide md:text-3xl",
        className,
      )}
      {...props}
    >
      {children}
    </h2>
  )
}
