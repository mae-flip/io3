import { expect, test } from "@playwright/test"

import { gotoWithAgeGate } from "./utils/ageGate"

test.use({ storageState: { cookies: [], origins: [] } })

test("Age gate is shown before site content", async ({ page }) => {
  await page.goto("/")
  await expect(
    page.getByRole("heading", { name: "18+ content warning" }),
  ).toBeVisible()
  await expect(
    page.getByRole("heading", { name: "Welcome to Our Index" }),
  ).not.toBeVisible()
})

test("Home page is accessible after accepting age gate", async ({ page }) => {
  await gotoWithAgeGate(page, "/")
  await expect(
    page.getByRole("heading", { name: "Welcome to Our Index" }),
  ).toBeVisible()
  await expect(
    page.getByRole("heading", { name: "Weekly Features" }),
  ).toBeVisible()
  await expect(page.getByRole("heading", { name: "Full Index" })).toBeVisible()
})

test("Homepage sort tabs are visible", async ({ page }) => {
  await gotoWithAgeGate(page, "/")
  await expect(page.getByRole("button", { name: "Latest" })).toBeVisible()
  await expect(page.getByRole("button", { name: "A>Z" })).toBeVisible()
  await expect(page.getByRole("button", { name: "Author A>Z" })).toBeVisible()
  await expect(page.getByRole("button", { name: "Kudos" })).toBeVisible()
})

test("Sort tab updates URL search params", async ({ page }) => {
  await gotoWithAgeGate(page, "/")
  await page.getByRole("button", { name: "A>Z" }).click()
  await expect(page).toHaveURL(/sort=title/)
})

test("Header search updates URL and scrolls to index", async ({ page }) => {
  await gotoWithAgeGate(page, "/")
  const searchInput = page.getByPlaceholder("Search games, authors, tags")
  await searchInput.fill("hornet")
  await page.getByRole("button", { name: "Search" }).click()
  await expect(page).toHaveURL(/search=hornet/)
  await expect(page.locator("#full-index")).toBeInViewport()
})

test("Header search is visible", async ({ page }) => {
  await gotoWithAgeGate(page, "/")
  await expect(
    page.getByPlaceholder("Search games, authors, tags"),
  ).toBeVisible()
})

test("Weekly features newsletter signup is visible", async ({ page }) => {
  await gotoWithAgeGate(page, "/")
  await expect(
    page.getByText("Get new weekly features in your inbox."),
  ).toBeVisible()
  await expect(page.getByRole("button", { name: "Subscribe" })).toBeVisible()
  await expect(page.getByPlaceholder("you@domain.com")).toBeVisible()
})

test("Age gate is remembered after acceptance", async ({ page }) => {
  await gotoWithAgeGate(page, "/")
  await page.reload()
  await expect(
    page.getByRole("heading", { name: "Welcome to Our Index" }),
  ).toBeVisible()
  await expect(
    page.getByRole("heading", { name: "18+ content warning" }),
  ).not.toBeVisible()
})

test("Submit nav link reaches submit page", async ({ page }) => {
  await gotoWithAgeGate(page, "/")
  await page.getByRole("link", { name: "SUBMIT TO IO3" }).click()
  await expect(page).toHaveURL(/\/submit/)
  await expect(
    page.getByRole("heading", { name: "Submit to io3" }),
  ).toBeVisible()
  await expect(
    page.getByRole("button", { name: "Log in with itch.io" }),
  ).toBeVisible()
})
