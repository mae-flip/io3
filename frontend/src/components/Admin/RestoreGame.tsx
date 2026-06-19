import { useMutation, useQueryClient } from "@tanstack/react-query"

import { AdminService } from "@/client"
import { Button } from "@/components/retroui/Button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface RestoreGameProps {
  id: string
  title?: string | null
}

export default function RestoreGame({ id, title }: RestoreGameProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () => AdminService.restoreAdminGame({ id }),
    onSuccess: () => {
      showSuccessToast(`${title || "Game"} restored to the index`)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["adminGames"] })
      queryClient.invalidateQueries({ queryKey: ["adminRemovedGames"] })
      queryClient.invalidateQueries({ queryKey: ["games"] })
    },
  })

  return (
    <Button
      type="button"
      variant="default"
      size="sm"
      className="font-head-sm uppercase tracking-wide"
      disabled={mutation.isPending}
      onClick={() => mutation.mutate()}
    >
      {mutation.isPending ? "Restoring…" : "Restore"}
    </Button>
  )
}
