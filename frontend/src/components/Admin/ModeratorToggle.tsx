import { useMutation, useQueryClient } from "@tanstack/react-query"

import { AdminService, type ModeratorUserPublic } from "@/client"
import { Checkbox } from "@/components/ui/checkbox"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

type ModeratorToggleProps = {
  user: ModeratorUserPublic
  disabled?: boolean
}

export function ModeratorToggle({ user, disabled }: ModeratorToggleProps) {
  const queryClient = useQueryClient()
  const { showErrorToast, showSuccessToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (isModerator: boolean) =>
      AdminService.updateAdminUser({
        userId: user.id,
        requestBody: { is_moderator: isModerator },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminUsers"] })
      showSuccessToast("Moderator access updated")
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Checkbox
      checked={Boolean(user.is_moderator)}
      disabled={disabled || mutation.isPending}
      onCheckedChange={(checked) => {
        mutation.mutate(checked === true)
      }}
      aria-label={`Moderator access for ${user.itch_username ?? user.id}`}
    />
  )
}
