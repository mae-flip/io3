import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"

import { UsersService } from "@/client"
import { Button } from "@/components/retroui/Button"
import { Input } from "@/components/retroui/Input"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface ContactEmailSectionProps {
  contactEmail?: string | null
}

export function ContactEmailSection({ contactEmail }: ContactEmailSectionProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const savedEmail = contactEmail ?? ""
  const [email, setEmail] = useState(savedEmail)

  useEffect(() => {
    setEmail(savedEmail)
  }, [savedEmail])

  const isDirty = email.trim() !== savedEmail

  const saveMutation = useMutation({
    mutationFn: (address: string) =>
      UsersService.updateUserContactEmail({
        requestBody: { email: address },
      }),
    onSuccess: (data) => {
      queryClient.setQueryData(["currentUser"], data)
      showSuccessToast("Contact email saved")
    },
    onError: handleError.bind(showErrorToast),
  })

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (saveMutation.isPending || !email.trim() || !isDirty) return
    saveMutation.mutate(email.trim())
  }

  return (
    <div className="flex flex-col gap-4 border-t-2 border-black/10 pt-6">
      <div className="flex flex-col gap-2">
        <h3 className="font-head-sm text-sm uppercase tracking-wide md:text-base">
          Contact email
        </h3>
        <p className="font-sans text-sm leading-snug text-dark-grey md:text-base">
          itch.io does not share your email with io3. We use this address to reach
          you about submissions and your indexed games.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-3 sm:flex-row sm:items-end"
      >
        <div className="grid min-w-0 flex-1 gap-1">
          <label
            htmlFor="profile-contact-email"
            className="font-sans text-xs uppercase tracking-wide text-dark-grey"
          >
            Email address
          </label>
          <Input
            id="profile-contact-email"
            type="email"
            name="email"
            autoComplete="email"
            required
            placeholder="you@domain.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>
        <Button
          type="submit"
          variant="pink"
          size="md"
          className="shrink-0 font-head-sm uppercase tracking-wide"
          disabled={!isDirty || saveMutation.isPending}
        >
          {saveMutation.isPending ? "Saving…" : "Save email"}
        </Button>
      </form>
    </div>
  )
}
