import type { SubmitBatchResponse } from "@/client"
import { Card } from "@/components/retroui/Card"
import { cn } from "@/lib/utils"

const statusLabels: Record<string, string> = {
  submitted: "Submitted",
  duplicate: "Already indexed",
  not_owned: "Not owned",
  still_listed: "Listed on itch.io",
  not_public: "Not public",
  error: "Error",
}

const statusColors: Record<string, string> = {
  submitted: "bg-green-100 text-green-900",
  duplicate: "bg-light-grey text-dark-grey",
  not_owned: "bg-orange/20 text-orange",
  still_listed: "bg-orange/20 text-orange",
  not_public: "bg-orange/20 text-orange",
  error: "bg-pink/20 text-pink",
}

export function SubmitResults({ results }: { results: SubmitBatchResponse }) {
  if (results.results.length === 0) return null

  return (
    <Card className="p-4 md:p-6">
      <h2 className="font-head text-xl uppercase">Submission results</h2>
      <p className="mt-1 text-sm text-dark-grey">
        {results.submitted_count} submitted, {results.skipped_count} skipped
      </p>
      <ul className="mt-4 space-y-2">
        {results.results.map((item) => (
          <li
            key={item.url}
            className="flex flex-wrap items-center justify-between gap-2 border-2 border-black bg-white px-3 py-2 text-sm"
          >
            <span className="min-w-0 truncate font-medium">{item.url}</span>
            <span
              className={cn(
                "shrink-0 border border-black px-2 py-0.5 text-xs uppercase",
                statusColors[item.status] ?? "bg-light-grey",
              )}
            >
              {statusLabels[item.status] ?? item.status}
            </span>
          </li>
        ))}
      </ul>
      {results.submitted_count > 0 && (
        <p className="mt-4 text-sm text-dark-grey">
          Submitted games are now live in the index.
        </p>
      )}
    </Card>
  )
}
