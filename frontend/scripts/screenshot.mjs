import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";

const BASE = "http://localhost:3000";
const OUT = "screenshots";
mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
page.on("console", (m) => { if (m.type() === "error") console.log("  [console.error]", m.text()); });

async function shot(name) {
  await page.waitForTimeout(1800);
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: true });
  console.log("captured:", name, "→", page.url());
}

// Login
await page.goto(`${BASE}/login`);
await page.getByLabel("Email").fill("partner@upstream.test");
await page.getByLabel("Password").fill("Passw0rd!");
await page.getByRole("button", { name: "Sign in" }).click();
await page.waitForURL("**/dashboard", { timeout: 15000 });
await shot("01-dashboard");

await page.goto(`${BASE}/companies`);
await shot("02-companies");

// Open the first company row
const firstRow = page.locator("table tbody tr").first();
if (await firstRow.count()) {
  await firstRow.click();
  await page.waitForURL(/\/companies\/\d+$/, { timeout: 10000 }).catch(() => {});
  await shot("03-company-detail");
}

await page.goto(`${BASE}/schedule`);
await shot("04-schedule");

await page.goto(`${BASE}/contacts`);
await shot("05-contacts");

await page.goto(`${BASE}/mandates`);
await shot("06-mandates");

// Open first mandate
const firstMandate = page.locator("table tbody tr").first();
if (await firstMandate.count()) {
  await firstMandate.click();
  await page.waitForURL(/\/mandates\/\d+$/, { timeout: 10000 }).catch(() => {});
  await shot("07-mandate-detail");
}

await page.goto(`${BASE}/analytics`);
await shot("08-analytics");

await page.goto(`${BASE}/settings`);
await shot("09-settings");

await browser.close();
console.log("DONE");
