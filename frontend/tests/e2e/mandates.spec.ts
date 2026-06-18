/**
 * Phase 7 — E2E: mandate lifecycle (create → appears → archive → hidden → restore).
 *
 * Requires both servers running + seeded DB (see cadence.spec.ts header).
 * Run with: npm run test:e2e
 */

import { expect, test } from "@playwright/test";

const PARTNER_EMAIL = "partner@upstream.test";
const PASSWORD = "Passw0rd!";

test.describe("Mandate management (partner)", () => {
  test("partner creates, archives, and restores a mandate", async ({ page }) => {
    const name = `E2E Mandate ${Date.now()}`;

    await page.goto("/login");
    await page.getByLabel("Email").fill(PARTNER_EMAIL);
    await page.getByLabel("Password").fill(PASSWORD);
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page).toHaveURL("/dashboard");

    // Create a mandate
    await page.goto("/mandates");
    await page.getByRole("button", { name: "New mandate" }).click();
    await page.getByLabel(/Client/).fill("E2E Client");
    await page.getByLabel(/Mandate name/).fill(name);
    await page.getByRole("button", { name: "Save" }).click();

    // It shows in the list
    await expect(page.getByText(name).first()).toBeVisible();

    // Open it and archive
    await page.getByText(name).first().click();
    await expect(page).toHaveURL(/\/mandates\/\d+$/);
    page.once("dialog", (d) => d.accept()); // confirm()
    await page.getByRole("button", { name: "Archive" }).click();
    await expect(page.getByText("Archived").first()).toBeVisible();

    // Restore it
    await page.getByRole("button", { name: "Restore" }).click();
    await expect(page.getByText("Archived")).toHaveCount(0);
  });
});
