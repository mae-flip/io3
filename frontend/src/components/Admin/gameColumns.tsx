import type { ColumnDef } from "@tanstack/react-table"

import type { AdminGamePublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import DeleteGame from "./DeleteGame"
import FeatureGameToggle from "./FeatureGameToggle"

const statusVariant: Record<
  AdminGamePublic["status"],
  "default" | "secondary" | "destructive" | "outline"
> = {
  approved: "default",
  pending: "secondary",
  rejected: "destructive",
  archived: "outline",
}

export const gameColumns: ColumnDef<AdminGamePublic>[] = [
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
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => (
      <Badge variant={statusVariant[row.original.status]}>
        {row.original.status}
      </Badge>
    ),
  },
  {
    id: "featured",
    header: "Featured",
    cell: ({ row }) => <FeatureGameToggle game={row.original} />,
  },
  {
    accessorKey: "created_at",
    header: "Added",
    cell: ({ row }) =>
      row.original.created_at
        ? new Date(row.original.created_at).toLocaleDateString()
        : "—",
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <DeleteGame id={row.original.id} title={row.original.title} />
      </div>
    ),
  },
]
