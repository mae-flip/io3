import { Link, useNavigate, useRouterState } from "@tanstack/react-router"
import { ChevronDown } from "lucide-react"
import { useEffect, useState } from "react"

import { PixelIcon } from "@/components/Common/PixelIcon"
import { ItchLoginButton } from "@/components/Submit/ItchLoginButton"
import { Input } from "@/components/retroui/Input"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import useCurrentUser, { isLoggedIn } from "@/hooks/useAuth"
import { useItchSubmit } from "@/hooks/useItchSubmit"
import { cn } from "@/lib/utils"

type NavLink =
  | { href: string; label: string; disabled?: boolean }
  | { to: string; label: string; disabled?: boolean }

const navLinks: NavLink[] = [
  { href: "#weekly-features", label: "Weekly Features", disabled: true },
  { href: "#about", label: "About Us", disabled: true },
  { to: "/submit", label: "SUBMIT TO IO3" },
]

function NavAuth({ className }: { className?: string }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname })
  const { user, isLoading, logout } = useCurrentUser()
  const { itchUsername, clearSession } = useItchSubmit()
  const loggedIn = isLoggedIn()

  if (loggedIn) {
    const name = user?.display_name || user?.itch_username || itchUsername
    if (!name && isLoading) return null

    return (
      <div className={cn("shrink-0", className)}>
        <DropdownMenu modal={false}>
          <DropdownMenuTrigger asChild>
            <button
              type="button"
              className="inline-flex flex-nowrap items-center gap-0.5 whitespace-nowrap font-head-sm text-sm text-white tracking-wide hover:underline md:text-base"
              aria-label="Account menu"
            >
              {name || "Account"}
              <ChevronDown className="size-4 shrink-0" aria-hidden />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link to="/profile">Edit profile</Link>
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => {
                logout()
                clearSession()
              }}
            >
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    )
  }

  return (
    <div className={cn("shrink-0", className)}>
      <ItchLoginButton
        returnTo={pathname}
        size="sm"
        className="whitespace-nowrap"
      />
    </div>
  )
}

interface PublicNavProps {
  showSearch?: boolean
}

export function PublicNav({ showSearch = true }: PublicNavProps) {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 0)
    onScroll()
    window.addEventListener("scroll", onScroll, { passive: true })
    return () => window.removeEventListener("scroll", onScroll)
  }, [])

  return (
    <header className="sticky top-0 z-50">
      <div
        className={cn(
          scrolled
            ? "relative left-1/2 w-screen -translate-x-1/2 bg-orange md:h-[var(--site-header-height)]"
            : "-ml-[var(--site-frame-padding)] w-[calc(100%+var(--site-frame-padding))] bg-orange pl-[var(--site-frame-padding)] md:h-[var(--site-header-height)] md:bg-transparent",
        )}
      >
        <div className="flex h-full flex-col gap-3 px-4 py-3 md:flex-row md:items-center md:gap-6 md:px-6 md:py-0">
          <div className="flex items-center justify-between gap-3 md:contents">
            <Link
              to="/"
              className="shrink-0 font-head text-3xl tracking-wide text-white uppercase md:text-4xl"
            >
              Index of Our Own
            </Link>
            <NavAuth className="md:hidden" />
          </div>

          {showSearch ? (
            <SearchBar className="min-w-0 flex-1" />
          ) : (
            <div className="hidden min-w-0 flex-1 md:block" aria-hidden />
          )}

          <div
            className={cn(
              "ml-6 flex shrink-0 flex-wrap items-center gap-4 md:ml-10 md:gap-6",
              scrolled ? "md:pr-6" : "md:pr-10 lg:pr-14",
            )}
          >
            <nav className="flex flex-wrap items-center gap-4 md:gap-6">
              {navLinks.map((link) => {
                const className = cn(
                  "font-head-sm text-sm uppercase tracking-wide md:text-base",
                  link.disabled
                    ? "cursor-not-allowed text-white/40"
                    : "text-white hover:underline",
                )

                if (link.disabled && "href" in link) {
                  return (
                    <span
                      key={link.label}
                      aria-disabled="true"
                      className={className}
                    >
                      {link.label}
                    </span>
                  )
                }

                return "href" in link ? (
                  <a key={link.label} href={link.href} className={className}>
                    {link.label}
                  </a>
                ) : (
                  <Link key={link.label} to={link.to} className={className}>
                    {link.label}
                  </Link>
                )
              })}
            </nav>
            <NavAuth className="hidden md:block" />
          </div>
        </div>
      </div>
    </header>
  )
}

export function SearchBar({ className }: { className?: string }) {
  const navigate = useNavigate({ from: "/" })
  const searchStr = useRouterState({ select: (s) => s.location.searchStr })
  const defaultValue = new URLSearchParams(searchStr).get("search") ?? ""

  return (
    <form
      className={cn("relative min-w-0 w-full", className)}
      onSubmit={(event) => {
        event.preventDefault()
        const formData = new FormData(event.currentTarget)
        const query = String(formData.get("search") ?? "").trim()
        navigate({
          search: (prev) => ({
            ...prev,
            search: query || undefined,
            skip: 0,
          }),
        })
        const index = document.getElementById("full-index")
        index?.scrollIntoView({ behavior: "smooth" })
      }}
    >
      <Input
        key={defaultValue}
        name="search"
        placeholder="Search games, authors, tags"
        className="h-11 pr-12 placeholder:text-dark-grey"
        defaultValue={defaultValue}
      />
      <button
        type="submit"
        className="absolute top-1/2 right-3 -translate-y-1/2 text-black"
        aria-label="Search"
      >
        <PixelIcon name="search" size={20} />
      </button>
    </form>
  )
}
