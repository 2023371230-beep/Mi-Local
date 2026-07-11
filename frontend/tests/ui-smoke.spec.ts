import { expect, test } from "@playwright/test";
import path from "node:path";

const routes = [
  { path: "/", name: "dashboard" },
  { path: "/chat", name: "chat" },
  { path: "/skills", name: "skills" },
  { path: "/rag", name: "rag" },
  { path: "/documents", name: "documents" },
  { path: "/models", name: "models" },
  { path: "/logs", name: "logs" },
  { path: "/agent", name: "agent" },
  { path: "/settings", name: "settings" },
];

test.describe("Chat composer menus", () => {
  test("los menus + y skill abren sin errores", async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on("console", (message) => {
      if (message.type() === "error") consoleErrors.push(message.text());
    });
    page.on("pageerror", (error) => consoleErrors.push(`PAGEERROR: ${error.message}`));

    await page.goto("/chat");
    await page.waitForLoadState("networkidle");

    await page.getByLabel("Mas opciones").click();
    await expect(page.getByText("Ingestar documentos")).toBeVisible();
    await page.keyboard.press("Escape");

    await page.getByLabel("Elegir skill").click();
    await expect(page.getByText("Ciberseguridad")).toBeVisible();
    await page.keyboard.press("Escape");

    expect(consoleErrors.filter((item) => !item.includes("favicon")).slice(0, 3)).toEqual([]);
  });
});

test.describe("UI smoke screenshots", () => {
  for (const route of routes) {
    test(`${route.name} renders`, async ({ page }, testInfo) => {
      const consoleErrors: string[] = [];
      page.on("console", (message) => {
        if (message.type() === "error") consoleErrors.push(message.text());
      });

      await page.goto(route.path);
      await page.waitForLoadState("networkidle");

      await expect(page.locator("body")).toBeVisible();
      await expect(page.getByText("Unhandled Runtime Error")).toHaveCount(0);
      await expect(page.getByText("Build Error")).toHaveCount(0);
      await expect(page.getByText("Application error")).toHaveCount(0);

      const suffix = testInfo.project.name === "mobile" ? "-mobile" : "";
      await page.screenshot({
        path: path.join("test-results", "ui-screenshots", `${route.name}${suffix}.png`),
        fullPage: true,
      });

      expect(consoleErrors.filter((item) => !item.includes("favicon")).slice(0, 3)).toEqual([]);
    });
  }
});
