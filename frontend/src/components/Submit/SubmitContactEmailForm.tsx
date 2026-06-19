import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"

import { UsersService } from "@/client"
import { Button } from "@/components/retroui/Button"
import { Card } from "@/components/retroui/Card"
import { Input } from "@/components/retroui/Input"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

type SubmitContactEmailFormProps = {
  itchUsername: string
}

export function SubmitContactEmailForm({
  itchUsername,
}: SubmitContactEmailFormProps) {
  const [email, setEmail] = useState("")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (address: string) =>
      UsersService.updateUserContactEmail({
        requestBody: { email: address },
      }),
    onSuccess: () => {
      showSuccessToast("Contact email saved.")
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (mutation.isPending || !email.trim()) return
    mutation.mutate(email.trim())
  }

  return (
    <div className="mx-auto flex max-w-xl flex-col gap-6">
      <div>
        <h1 className="font-head text-3xl uppercase">Submit to io3</h1>
        <p className="mt-2 text-dark-grey">
          Logged in as{" "}
          <span className="font-medium text-black">{itchUsername}</span>. Add a
          contact email before you can submit games.
        </p>
      </div>

      <Card className="flex flex-col gap-4 p-6">
        <div>
          <h2 className="font-head-sm text-sm uppercase">Contact email</h2>
          <p className="mt-1 text-sm text-dark-grey">
            itch.io does not share your email with io3. We need an address so we
            can reach you about submissions and your indexed games.
          </p>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <label htmlFor="submit-contact-email" className="sr-only">
            Email address
          </label>
          <Input
            id="submit-contact-email"
            type="email"
            name="email"
            autoComplete="email"
            required
            placeholder="you@domain.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <Button
            type="submit"
            variant="pink"
            size="lg"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Saving…" : "Continue to game picker"}
          </Button>
        </form>
      </Card>
    </div>
  )
}
