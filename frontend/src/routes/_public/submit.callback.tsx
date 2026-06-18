import { useMutation, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect, useRef } from "react"

import { ItchAuthService } from "@/client"
import { Card } from "@/components/retroui/Card"
import { useItchSubmit } from "@/hooks/useItchSubmit"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_public/submit/callback")({
  component: SubmitCallbackPage,
})

function SubmitCallbackPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { setSession, consumeOAuthState, consumeOAuthReturnTo } = useItchSubmit()
  const { showErrorToast } = useCustomToast()
  const started = useRef(false)

  const mutation = useMutation({
    mutationFn: (payload: { access_token: string; state: string }) =>
      ItchAuthService.itchCallback({ requestBody: payload }),
    onSuccess: (data, variables) => {
      const returnTo = consumeOAuthReturnTo()
      setSession({
        io3Token: data.access_token,
        itchAccessToken: variables.access_token,
        games: data.games,
        itchUsername: data.itch_username,
      })
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      navigate({ to: returnTo })
    },
    onError: handleError.bind(showErrorToast),
  })

  useEffect(() => {
    if (started.current) return
    started.current = true

    const hash = window.location.hash.startsWith("#")
      ? window.location.hash.slice(1)
      : window.location.hash
    const params = new URLSearchParams(hash)
    const accessToken = params.get("access_token")
    const returnedState = params.get("state")
    const storedState = consumeOAuthState()

    if (!accessToken) {
      showErrorToast("No itch.io credentials received. Please try again.")
      navigate({ to: consumeOAuthReturnTo() })
      return
    }

    if (!returnedState || returnedState !== storedState) {
      showErrorToast("OAuth state mismatch. Please try logging in again.")
      navigate({ to: consumeOAuthReturnTo() })
      return
    }

    window.history.replaceState(null, "", window.location.pathname)
    mutation.mutate({ access_token: accessToken, state: returnedState })
    // eslint-disable-next-line react-hooks/exhaustive-deps -- run once on mount
  }, [])

  return (
    <Card className="mx-auto max-w-md p-8 text-center">
      <p className="font-head text-lg uppercase">Connecting itch.io…</p>
      <p className="mt-2 text-sm text-dark-grey">
        {mutation.isPending ? "Verifying your account." : "Redirecting…"}
      </p>
    </Card>
  )
}
