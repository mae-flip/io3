import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { type UserPublic, UsersService } from "@/client"
import { handleError } from "@/utils"
import useCustomToast from "./useCustomToast"

export const isLoggedIn = () => {
  return localStorage.getItem("access_token") !== null
}

const useCurrentUser = () => {
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

  const { data: user, isLoading, isError } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
    enabled: isLoggedIn(),
    retry: false,
  })

  const logoutMutation = useMutation({
    mutationFn: async () => {
      localStorage.removeItem("access_token")
      sessionStorage.removeItem("itch_access_token")
      sessionStorage.removeItem("itch_games")
      sessionStorage.removeItem("itch_username")
      sessionStorage.removeItem("itch_oauth_state")
      sessionStorage.removeItem("oauth_return_to")
    },
    onSuccess: () => {
      queryClient.setQueryData(["currentUser"], null)
      queryClient.invalidateQueries({ queryKey: ["games"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const isOwner = Boolean(user?.is_owner)
  const isModerator = Boolean(user?.is_moderator)
  const canAccessAdmin = isOwner || isModerator

  return {
    user,
    isLoading,
    isError,
    isOwner,
    isModerator,
    canAccessAdmin,
    logout: logoutMutation.mutate,
  }
}

export default useCurrentUser
