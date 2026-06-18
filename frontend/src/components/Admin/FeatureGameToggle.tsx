import { useMutation, useQueryClient } from "@tanstack/react-query"

import { AdminService, type AdminGamePublic } from "@/client"
import { Checkbox } from "@/components/ui/checkbox"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface FeatureGameToggleProps {
  game: AdminGamePublic
}

const FeatureGameToggle = ({ game }: FeatureGameToggleProps) => {
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()
  const isFeatured = game.featured_at != null
  const canFeature = game.status === "approved"

  const mutation = useMutation({
    mutationFn: () =>
      isFeatured
        ? AdminService.unfeatureAdminGame({ id: game.id })
        : AdminService.featureAdminGame({ id: game.id }),
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["adminGames"] })
      queryClient.invalidateQueries({ queryKey: ["games", "featured"] })
    },
  })

  return (
    <Checkbox
      checked={isFeatured}
      disabled={!canFeature || mutation.isPending}
      onCheckedChange={() => mutation.mutate()}
      aria-label={
        isFeatured ? `Remove ${game.title ?? "game"} from features` : "Feature game"
      }
    />
  )
}

export default FeatureGameToggle
