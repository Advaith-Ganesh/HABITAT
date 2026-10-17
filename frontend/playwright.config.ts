import { defineConfig } from "@playwright/test";
import { fileURLToPath } from "node:url";
import path from "node:path";
const root = fileURLToPath(new URL("..", import.meta.url));
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 90000,
  expect: { timeout: 12000 },
  reporter: [["list"], ["json", { outputFile: "../reports/v6-e2e.json" }]],
  use: {
    baseURL: "http://127.0.0.1:8001",
    viewport: { width: 1440, height: 1000 },
    headless: true,
    launchOptions:
      process.platform === "darwin"
        ? {
            executablePath:
              process.env.HABITAT_CHROME_PATH ??
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
          }
        : {},
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  webServer: {
    command:
      ".venv/bin/python -m scripts.prepare_e2e && .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001",
    cwd: root,
    url: "http://127.0.0.1:8001/health",
    reuseExistingServer: false,
    env: {
      HABITAT_DATABASE_URL:
        "sqlite:///" + path.join(root, ".test-runtime/browser.db"),
      MPLCONFIGDIR: path.join(root, ".test-runtime/matplotlib"),
    },
    timeout: 60000,
  },
});
