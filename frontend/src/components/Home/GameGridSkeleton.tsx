import { cn } from "@/lib/utils"

interface GameGridSkeletonProps {
  count?: number
  className?: string
}

export function GameGridSkeleton({
  count = 4,
  className,
}: GameGridSkeletonProps) {
  return (
    <div
      className={cn(
        "grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4",
        className,
      )}
      aria-hidden
    >
      {Array.from({ length: count }, (_, index) => (
        <div
          key={index}
          className="aspect-thumbnail animate-pulse border-2 border-black bg-light-grey"
        />
      ))}
    </div>
  )
}
