import type { ColumnDef } from "@tanstack/react-table"

import type { ModeratorUserPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

import { ModeratorToggle } from "./ModeratorToggle"

export type ModeratorTableData = ModeratorUserPublic & {
  isCurrentUser: boolean
}

export const moderatorColumns: ColumnDef<ModeratorTableData>[] = [
  {
    accessorKey: "itch_username",
    header: "itch.io user",
    cell: ({ row }) => {
      const username = row.original.itch_username
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn("font-medium", !username && "text-muted-foreground")}
          >
            {username || "N/A"}
          </span>
          {row.original.isCurrentUser && (
            <Badge variant="outline" className="text-xs">
              You
            </Badge>
          )}
        </div>
      )
    },
  },
  {
    accessorKey: "display_name",
    header: "Display name",
    cell: ({ row }) => (
      <span className="text-muted-foreground">
        {row.original.display_name || "—"}
      </span>
    ),
  },
  {
    id: "role",
    header: "Role",
    cell: ({ row }) => {
      if (row.original.is_owner) {
        return <Badge>Owner</Badge>
      }
      if (row.original.is_moderator) {
        return <Badge variant="default">Moderator</Badge>
      }
      return <Badge variant="secondary">User</Badge>
    },
  },
  {
    id: "moderator",
    header: "Moderator access",
    cell: ({ row }) => (
      <ModeratorToggle user={row.original} disabled={row.original.is_owner} />
    ),
  },
]
