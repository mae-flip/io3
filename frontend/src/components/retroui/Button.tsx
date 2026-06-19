import { cva, type VariantProps } from "class-variance-authority"
import type * as React from "react"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 border-2 border-black font-sans text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 shadow-md active:translate-x-[2px] active:translate-y-[2px] active:shadow-none",
  {
    variants: {
      variant: {
        default: "bg-white text-black hover:bg-light-grey",
        pink: "bg-pink text-white hover:bg-pink-light",
        orange: "bg-orange text-white",
        ghost:
          "border-transparent bg-transparent shadow-none hover:bg-white/20",
        link: "border-transparent bg-transparent p-0 shadow-none underline-offset-4 hover:underline",
      },
      size: {
        sm: "h-8 px-3 text-xs",
        md: "h-10 px-4",
        lg: "h-12 px-6 text-base",
        icon: "size-10 p-0",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  },
)

function Button({
  className,
  variant,
  size,
  ...props
}: React.ComponentProps<"button"> & VariantProps<typeof buttonVariants>) {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
