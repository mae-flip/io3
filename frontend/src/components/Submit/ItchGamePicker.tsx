import { useMutation } from "@tanstack/react-query"
import { useState } from "react"

import { ApiError, GamesService, type SubmitBatchResponse } from "@/client"
import { Button } from "@/components/retroui/Button"
import { Card } from "@/components/retroui/Card"
import { SubmitResults } from "@/components/Submit/SubmitResults"
import { useItchSubmit } from "@/hooks/useItchSubmit"
import useCustomToast from "@/hooks/useCustomToast"
import { cn } from "@/lib/utils"
import { handleError } from "@/utils"

function gameRowStatus(game: {
  published?: boolean
  already_indexed?: boolean
  itch_search_listed?: boolean
}): { label: string; className: string; disabled: boolean } {
  if (game.already_indexed) {
    return {
      label: "Already indexed on io3!",
      className: "bg-light-grey",
      disabled: true,
    }
  }
  if (game.itch_search_listed) {
    return {
      label: "Listed on itch",
      className: "bg-orange/20",
      disabled: true,
    }
  }
  if (game.published === false) {
    return {
      label: "Draft",
      className: "bg-orange/20",
      disabled: true,
    }
  }
  return {
    label: "Delisted",
    className: "bg-green-100",
    disabled: false,
  }
}

export function ItchGamePicker() {
  const { games, itchAccessToken, itchUsername, clearSession } = useItchSubmit()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [batchResults, setBatchResults] = useState<SubmitBatchResponse | null>(
    null,
  )

  const mutation = useMutation({
    mutationFn: (urls: string[]) =>
      GamesService.submitGamesBatch({
        requestBody: {
          urls,
          itch_access_token: itchAccessToken ?? "",
        },
      }),
    onSuccess: (data) => {
      setBatchResults(data)
      setSelected(new Set())
      if (data.submitted_count > 0) {
        showSuccessToast(
          `${data.submitted_count} game${data.submitted_count === 1 ? "" : "s"} added to the index`,
        )
      }
    },
    onError: (err: ApiError) => {
      handleError.call(showErrorToast, err)
      if (err.status === 401) {
        clearSession()
      }
    },
  })

  const toggle = (id: number, disabled: boolean) => {
    if (disabled) return
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const submitSelected = () => {
    const urls = games
      .filter((game) => selected.has(game.id))
      .map((game) => game.url)
    if (urls.length === 0) return
    mutation.mutate(urls)
  }

  const selectableCount = games.filter(
    (game) =>
      game.published !== false &&
      !game.already_indexed &&
      !game.itch_search_listed,
  ).length

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-head text-3xl uppercase">Submit to io3</h1>
          <p className="mt-1 text-sm text-dark-grey">
            Logged in as{" "}
            <span className="font-medium text-black">{itchUsername}</span>
            . Only de-listed games (not found in itch search) can be submitted.
          </p>
        </div>
        <Button type="button" variant="ghost" size="sm" onClick={clearSession}>
          Log out
        </Button>
      </div>

      <Card className="overflow-hidden">
        <div className="border-b-2 border-black bg-orange px-4 py-3">
          <h2 className="font-head-sm text-sm uppercase text-white">
            Your itch.io games
          </h2>
        </div>
        {games.length === 0 ? (
          <p className="p-4 text-sm text-dark-grey">
            No games found on your itch.io account.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead>
                <tr className="border-b-2 border-black bg-light-grey">
                  <th className="w-10 px-3 py-2" />
                  <th className="px-3 py-2 font-head-sm text-xs uppercase">
                    Game
                  </th>
                  <th className="px-3 py-2 font-head-sm text-xs uppercase">
                    URL
                  </th>
                  <th className="px-3 py-2 font-head-sm text-xs uppercase">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {games.map((game) => {
                  const status = gameRowStatus(game)
                  const checked = selected.has(game.id)
                  return (
                    <tr
                      key={game.id}
                      className={cn(
                        "border-b border-black/20",
                        status.disabled && "opacity-60",
                      )}
                    >
                      <td className="px-3 py-3">
                        <input
                          type="checkbox"
                          checked={checked}
                          disabled={status.disabled || mutation.isPending}
                          onChange={() => toggle(game.id, status.disabled)}
                          aria-label={`Select ${game.title}`}
                          className="size-4 accent-pink"
                        />
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex items-center gap-3">
                          {game.cover_url ? (
                            <img
                              src={game.cover_url}
                              alt=""
                              className="size-12 border border-black object-cover"
                            />
                          ) : (
                            <div className="size-12 border border-black bg-light-grey" />
                          )}
                          <div>
                            <p className="font-medium">{game.title}</p>
                            {game.short_text && (
                              <p className="line-clamp-1 text-xs text-dark-grey">
                                {game.short_text}
                              </p>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="max-w-[200px] truncate px-3 py-3 text-dark-grey">
                        <a
                          href={game.url}
                          target="_blank"
                          rel="noreferrer"
                          className="hover:underline"
                        >
                          {game.normalized_url ?? game.url}
                        </a>
                      </td>
                      <td className="px-3 py-3">
                        <span
                          className={cn(
                            "border border-black px-2 py-0.5 text-xs uppercase",
                            status.className,
                          )}
                        >
                          {status.label}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {selectableCount > 0 && (
        <div className="flex justify-end">
          <Button
            type="button"
            variant="pink"
            size="lg"
            disabled={selected.size === 0 || mutation.isPending}
            onClick={submitSelected}
          >
            {mutation.isPending
              ? "Submitting…"
              : `Submit ${selected.size || ""} game${selected.size === 1 ? "" : "s"}`.trim()}
          </Button>
        </div>
      )}

      {batchResults && <SubmitResults results={batchResults} />}
    </div>
  )
}
