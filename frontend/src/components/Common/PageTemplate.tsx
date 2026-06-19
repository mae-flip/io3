import { Link } from "@tanstack/react-router"
import { ChevronRight } from "lucide-react"
import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

export type PageBreadcrumb = {
  label: string
  to: string
}

interface PageTemplateProps {
  title: string
  description?: ReactNode
  breadcrumbs?: PageBreadcrumb[]
  children: ReactNode
  className?: string
}

function PageBreadcrumbs({
  crumbs,
  current,
}: {
  crumbs: PageBreadcrumb[]
  current: string
}) {
  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex flex-wrap items-center gap-1.5 font-sans text-sm text-dark-grey">
        <li>
          <Link to="/" className="hover:text-black hover:underline">
            Home
          </Link>
        </li>
        {crumbs.map((crumb) => (
          <li key={crumb.to} className="flex items-center gap-1.5">
            <ChevronRight className="size-3.5 shrink-0" aria-hidden />
            <Link to={crumb.to} className="hover:text-black hover:underline">
              {crumb.label}
            </Link>
          </li>
        ))}
        <li className="flex items-center gap-1.5">
          <ChevronRight className="size-3.5 shrink-0" aria-hidden />
          <span aria-current="page" className="text-black">
            {current}
          </span>
        </li>
      </ol>
    </nav>
  )
}

export function PageTemplate({
  title,
  description,
  breadcrumbs = [],
  children,
  className,
}: PageTemplateProps) {
  return (
    <div className={cn("flex flex-col gap-6", className)}>
      <div className="flex flex-col gap-3">
        <PageBreadcrumbs crumbs={breadcrumbs} current={title} />
        <div>
          <h1 className="font-head text-3xl tracking-wide uppercase md:text-4xl">
            {title}
          </h1>
          {description ? (
            <div className="mt-2 font-sans text-sm text-dark-grey md:text-base">
              {description}
            </div>
          ) : null}
        </div>
      </div>
      {children}
    </div>
  )
}
