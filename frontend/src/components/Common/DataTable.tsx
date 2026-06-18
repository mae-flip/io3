import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table"
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  rowCount?: number
  pageIndex?: number
  pageSize?: number
  onPageChange?: (pageIndex: number) => void
  onPageSizeChange?: (pageSize: number) => void
}

export function DataTable<TData, TValue>({
  columns,
  data,
  rowCount,
  pageIndex = 0,
  pageSize = 10,
  onPageChange,
  onPageSizeChange,
}: DataTableProps<TData, TValue>) {
  const manualPagination = rowCount !== undefined

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    ...(manualPagination
      ? {
          manualPagination: true,
          rowCount,
          pageCount: Math.max(1, Math.ceil(rowCount / pageSize)),
          state: {
            pagination: { pageIndex, pageSize },
          },
          onPaginationChange: (updater) => {
            const current = { pageIndex, pageSize }
            const next =
              typeof updater === "function" ? updater(current) : updater
            if (next.pageIndex !== pageIndex) {
              onPageChange?.(next.pageIndex)
            }
            if (next.pageSize !== pageSize) {
              onPageSizeChange?.(next.pageSize)
            }
          },
        }
      : {
          getPaginationRowModel: getPaginationRowModel(),
        }),
  })

  const totalEntries = manualPagination ? rowCount : data.length
  const currentPageIndex = manualPagination
    ? pageIndex
    : table.getState().pagination.pageIndex
  const currentPageSize = manualPagination
    ? pageSize
    : table.getState().pagination.pageSize
  const pageCount = manualPagination
    ? Math.max(1, Math.ceil(rowCount / pageSize))
    : table.getPageCount()
  const rangeStart = totalEntries === 0 ? 0 : currentPageIndex * currentPageSize + 1
  const rangeEnd = Math.min(
    (currentPageIndex + 1) * currentPageSize,
    totalEntries,
  )
  const showPagination = manualPagination
    ? totalEntries > currentPageSize
    : pageCount > 1

  return (
    <div className="flex flex-col gap-4">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id} className="hover:bg-transparent">
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                  </TableHead>
                )
              })}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow className="hover:bg-transparent">
              <TableCell
                colSpan={columns.length}
                className="h-32 text-center text-muted-foreground"
              >
                No results found.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {showPagination && (
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 border-t bg-muted/20">
          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            <div className="text-sm text-muted-foreground">
              Showing {rangeStart} to {rangeEnd} of{" "}
              <span className="font-medium text-foreground">{totalEntries}</span>{" "}
              entries
            </div>
            <div className="flex items-center gap-x-2">
              <p className="text-sm text-muted-foreground">Rows per page</p>
              <Select
                value={`${currentPageSize}`}
                onValueChange={(value) => {
                  if (manualPagination) {
                    onPageSizeChange?.(Number(value))
                  } else {
                    table.setPageSize(Number(value))
                  }
                }}
              >
                <SelectTrigger className="h-8 w-[70px]">
                  <SelectValue placeholder={currentPageSize} />
                </SelectTrigger>
                <SelectContent side="top">
                  {[5, 10, 25, 50].map((size) => (
                    <SelectItem key={size} value={`${size}`}>
                      {size}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex items-center gap-x-6">
            <div className="flex items-center gap-x-1 text-sm text-muted-foreground">
              <span>Page</span>
              <span className="font-medium text-foreground">
                {currentPageIndex + 1}
              </span>
              <span>of</span>
              <span className="font-medium text-foreground">{pageCount}</span>
            </div>

            <div className="flex items-center gap-x-1">
              <Button
                variant="outline"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={() => {
                  if (manualPagination) {
                    onPageChange?.(0)
                  } else {
                    table.setPageIndex(0)
                  }
                }}
                disabled={currentPageIndex <= 0}
              >
                <span className="sr-only">Go to first page</span>
                <ChevronsLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={() => {
                  if (manualPagination) {
                    onPageChange?.(currentPageIndex - 1)
                  } else {
                    table.previousPage()
                  }
                }}
                disabled={currentPageIndex <= 0}
              >
                <span className="sr-only">Go to previous page</span>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={() => {
                  if (manualPagination) {
                    onPageChange?.(currentPageIndex + 1)
                  } else {
                    table.nextPage()
                  }
                }}
                disabled={currentPageIndex + 1 >= pageCount}
              >
                <span className="sr-only">Go to next page</span>
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={() => {
                  if (manualPagination) {
                    onPageChange?.(pageCount - 1)
                  } else {
                    table.setPageIndex(pageCount - 1)
                  }
                }}
                disabled={currentPageIndex + 1 >= pageCount}
              >
                <span className="sr-only">Go to last page</span>
                <ChevronsRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
