import { useSuspenseQuery } from "@tanstack/react-query"
import { Suspense } from "react"

import { AdminService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import PendingGames from "@/components/Pending/PendingGames"
import useCurrentUser from "@/hooks/useAuth"

import { moderatorColumns } from "./moderatorColumns"

function getAdminUsersQueryOptions() {
  return {
    queryFn: () => AdminService.readAdminUsers({ skip: 0, limit: 500 }),
    queryKey: ["adminUsers"],
  }
}

function ModeratorsTableContent() {
  const { user: currentUser } = useCurrentUser()
  const { data: users } = useSuspenseQuery(getAdminUsersQueryOptions())
  const tableData = users.data.map((user) => ({
    ...user,
    isCurrentUser: user.id === currentUser?.id,
  }))

  return <DataTable columns={moderatorColumns} data={tableData} />
}

export function ModeratorsTable() {
  return (
    <Suspense fallback={<PendingGames />}>
      <ModeratorsTableContent />
    </Suspense>
  )
}
