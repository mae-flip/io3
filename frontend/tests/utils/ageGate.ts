import type { Page } from "@playwright/test"

export async function acceptAgeGate(page: Page) {
  const enterButton = page.getByRole("button", {
    name: "I am 18 or older — enter",
  })
  if (await enterButton.isVisible()) {
    await enterButton.click()
  }
}

export async function gotoWithAgeGate(page: Page, path: string) {
  await page.goto(path)
  await acceptAgeGate(page)
}
