import { expect, test } from "@playwright/test"

import { gotoWithAgeGate } from "./utils/ageGate"

test.use({ storageState: { cookies: [], origins: [] } })

test("Admin page shows itch login when not authenticated", async ({ page }) => {
  await gotoWithAgeGate(page, "/admin")
  await expect(page.getByRole("heading", { name: "Admin" })).toBeVisible()
  await expect(
    page.getByRole("button", { name: "Log in with itch.io" }),
  ).toBeVisible()
})
