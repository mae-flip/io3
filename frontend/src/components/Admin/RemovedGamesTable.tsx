import { useQuery } from "@tanstack/react-query"
import { useEffect, useState } from "react"

import { AdminService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import PendingGames from "@/components/Pending/PendingGames"
import { Input } from "@/components/retroui/Input"

import { removedGameColumns } from "./removedGameColumns"

const DEFAULT_PAGE_SIZE = 10

export function RemovedGamesTable() {
  const [search, setSearch] = useState("")
  const [debouncedSearch, setDebouncedSearch] = useState("")
  const [pageIndex, setPageIndex] = useState(0)
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE)

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setDebouncedSearch(search)
      setPageIndex(0)
    }, 300)
    return () => window.clearTimeout(timeout)
  }, [search])

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ["adminRemovedGames", debouncedSearch, pageIndex, pageSize],
    queryFn: () =>
      AdminService.readRemovedAdminGames({
        skip: pageIndex * pageSize,
        limit: pageSize,
        search: debouncedSearch || undefined,
      }),
  })

  const totalCount = data?.count ?? 0

  return (
    <div className="flex flex-col gap-4">
      <Input
        type="search"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        placeholder="Search removed games…"
        aria-label="Search removed games"
        className="max-w-md"
      />
      {isLoading ? (
        <PendingGames />
      ) : totalCount === 0 ? (
        <p className="text-sm text-muted-foreground">No removed games.</p>
      ) : (
        <div
          className={isFetching ? "opacity-60 transition-opacity" : undefined}
        >
          <DataTable
            columns={removedGameColumns}
            data={data?.data ?? []}
            rowCount={totalCount}
            pageIndex={pageIndex}
            pageSize={pageSize}
            onPageChange={setPageIndex}
            onPageSizeChange={(nextPageSize) => {
              setPageSize(nextPageSize)
              setPageIndex(0)
            }}
          />
        </div>
      )}
    </div>
  )
}
