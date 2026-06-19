import { useMutation } from "@tanstack/react-query"
import type { VariantProps } from "class-variance-authority"
import { FaItchIo } from "react-icons/fa6"

import { ItchAuthService } from "@/client"
import { Button, type buttonVariants } from "@/components/retroui/Button"
import useCustomToast from "@/hooks/useCustomToast"
import { useItchSubmit } from "@/hooks/useItchSubmit"
import { cn } from "@/lib/utils"
import { handleError } from "@/utils"

type ItchLoginButtonProps = {
  returnTo?: string
  size?: VariantProps<typeof buttonVariants>["size"]
  className?: string
}

export function ItchLoginButton({
  returnTo = "/submit",
  size = "lg",
  className,
}: ItchLoginButtonProps) {
  const { storeOAuthState, storeOAuthReturnTo } = useItchSubmit()
  const { showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () => ItchAuthService.itchAuthorize(),
    onSuccess: (data) => {
      storeOAuthReturnTo(returnTo)
      storeOAuthState(data.state)
      window.location.href = data.authorize_url
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Button
      type="button"
      variant="pink"
      size={size}
      className={cn(className)}
      disabled={mutation.isPending}
      onClick={() => mutation.mutate()}
    >
      {mutation.isPending ? (
        "Connecting…"
      ) : (
        <>
          <FaItchIo className="size-4 shrink-0" aria-hidden />
          Log in with itch.io
        </>
      )}
    </Button>
  )
}
