import { useMutation } from "@tanstack/react-query"
import { useState } from "react"

import { NewsletterService } from "@/client"
import { Button } from "@/components/retroui/Button"
import { Input } from "@/components/retroui/Input"
import useCustomToast from "@/hooks/useCustomToast"

export function NewsletterSubscribeForm() {
  const [email, setEmail] = useState("")
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const subscribeMutation = useMutation({
    mutationFn: (address: string) =>
      NewsletterService.subscribeToNewsletter({
        requestBody: { email: address },
      }),
    onSuccess: (data) => {
      showSuccessToast(data.message)
      setEmail("")
    },
    onError: () => {
      showErrorToast("Please enter a valid email address.")
    },
  })

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (subscribeMutation.isPending || !email.trim()) return
    subscribeMutation.mutate(email.trim())
  }

  return (
    <div className="border-t-2 border-black/20 pt-6">
      <p className="mb-3 font-sans text-sm text-pink-light md:text-base">
        Get new weekly features in your inbox.
      </p>
      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-3 sm:flex-row sm:items-center"
      >
        <label htmlFor="newsletter-email" className="sr-only">
          Email address
        </label>
        <Input
          id="newsletter-email"
          type="email"
          name="email"
          autoComplete="email"
          required
          placeholder="you@domain.com"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="min-w-0 flex-1 bg-white"
        />
        <Button
          type="submit"
          variant="default"
          size="lg"
          disabled={subscribeMutation.isPending}
          className="shrink-0 font-head-sm uppercase tracking-wide"
        >
          {subscribeMutation.isPending ? "Subscribing..." : "Subscribe"}
        </Button>
      </form>
    </div>
  )
}
