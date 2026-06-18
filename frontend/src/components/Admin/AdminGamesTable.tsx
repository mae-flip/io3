import { useQuery } from "@tanstack/react-query"
import { useEffect, useState } from "react"

import { AdminService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import PendingGames from "@/components/Pending/PendingGames"
import { Input } from "@/components/retroui/Input"

import { gameColumns } from "./gameColumns"

const DEFAULT_PAGE_SIZE = 10

export function AdminGamesTable() {
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
    queryKey: ["adminGames", debouncedSearch, pageIndex, pageSize],
    queryFn: () =>
      AdminService.readAdminGames({
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
        placeholder="Search by title, URL, or author…"
        aria-label="Search games"
        className="max-w-md"
      />
      {isLoading ? (
        <PendingGames />
      ) : (
        <div className={isFetching ? "opacity-60 transition-opacity" : undefined}>
          <DataTable
            columns={gameColumns}
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
