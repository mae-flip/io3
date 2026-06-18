import { expect, type Page } from "@playwright/test"

import { acceptAgeGate } from "./ageGate"

export async function signUpNewUser(
  page: Page,
  name: string,
  email: string,
  password: string,
) {
  await page.goto("/signup")
  await acceptAgeGate(page)

  await page.getByTestId("full-name-input").fill(name)
  await page.getByTestId("email-input").fill(email)
  await page.getByTestId("password-input").fill(password)
  await page.getByTestId("confirm-password-input").fill(password)
  await page.getByRole("button", { name: "Sign Up" }).click()
  await page.goto("/login")
}

export async function logInUser(page: Page, email: string, password: string) {
  await page.goto("/login")
  await acceptAgeGate(page)

  await page.getByTestId("email-input").fill(email)
  await page.getByTestId("password-input").fill(password)
  await page.getByRole("button", { name: "Log In" }).click()
  await page.waitForURL("/")
  await expect(
    page.getByRole("heading", { name: "Welcome to Our Index" }),
  ).toBeVisible()
}

export async function logOutUser(page: Page) {
  await page.evaluate(() => localStorage.removeItem("access_token"))
  await page.goto("/login")
  await acceptAgeGate(page)
}
