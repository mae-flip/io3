import { useQuery } from "@tanstack/react-query"

import { AdminService } from "@/client"
import { OpenAPI } from "@/client/core/OpenAPI"
import { Button } from "@/components/retroui/Button"
import { Card } from "@/components/retroui/Card"

async function downloadNewsletterSubscribersCsv() {
  const token = localStorage.getItem("access_token")
  const response = await fetch(
    `${OpenAPI.BASE}/api/v1/admin/newsletter/subscribers.csv`,
    {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    },
  )
  if (!response.ok) {
    throw new Error("Could not download subscriber list")
  }
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = "newsletter-subscribers.csv"
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export function NewsletterSubscribersCard() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "newsletterSubscribers"],
    queryFn: () => AdminService.readNewsletterSubscribers(),
  })

  return (
    <Card className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 className="font-head text-2xl tracking-wide uppercase">
          Email subscribers
        </h2>
        <p className="text-muted-foreground">
          {isLoading
            ? "Loading subscriber count…"
            : `${data?.count ?? 0} subscriber${data?.count === 1 ? "" : "s"}`}
        </p>
      </div>
      <Button
        type="button"
        onClick={() => {
          void downloadNewsletterSubscribersCsv()
        }}
      >
        Download csv of email subscribers
      </Button>
    </Card>
  )
}
