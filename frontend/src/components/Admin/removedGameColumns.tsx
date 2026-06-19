import type { ColumnDef } from "@tanstack/react-table"

import type { AdminGamePublic } from "@/client"
import { cn } from "@/lib/utils"

import RestoreGame from "./RestoreGame"

export const removedGameColumns: ColumnDef<AdminGamePublic>[] = [
  {
    accessorKey: "title",
    header: "Title",
    cell: ({ row }) => (
      <span
        className={cn(
          "font-medium",
          !row.original.title && "text-muted-foreground",
        )}
      >
        {row.original.title || "Untitled"}
      </span>
    ),
  },
  {
    accessorKey: "itch_url",
    header: "Itch URL",
    cell: ({ row }) => (
      <a
        href={row.original.itch_url}
        target="_blank"
        rel="noopener noreferrer"
        className="max-w-md truncate text-sm text-muted-foreground hover:underline"
      >
        {row.original.itch_url}
      </a>
    ),
  },
  {
    accessorKey: "updated_at",
    header: "Removed",
    cell: ({ row }) =>
      row.original.updated_at
        ? new Date(row.original.updated_at).toLocaleDateString()
        : "—",
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <RestoreGame id={row.original.id} title={row.original.title} />
      </div>
    ),
  },
]
