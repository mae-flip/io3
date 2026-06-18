import { cn } from "@/lib/utils"

export type SortOption = "latest" | "title" | "author" | "kudos"

const sortOptions: { value: SortOption; label: string }[] = [
  { value: "latest", label: "Latest" },
  { value: "title", label: "A>Z" },
  { value: "author", label: "Author A>Z" },
  { value: "kudos", label: "Kudos" },
]

interface SortTabsProps {
  value: SortOption
  onChange: (value: SortOption) => void
}

export function SortTabs({ value, onChange }: SortTabsProps) {
  return (
    <div className="flex flex-wrap items-center gap-4 border-b-2 border-black bg-light-grey px-4 py-3">
      {sortOptions.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          className={cn(
            "font-sans text-sm transition-colors",
            value === option.value
              ? "font-bold text-black"
              : "text-dark-grey hover:text-black",
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}
