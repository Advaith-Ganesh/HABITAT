import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("Applicant to administrator to applicant: persistent review", async ({
  page,
  request,
}) => {
  await page.goto("/#applicant/Apply%20for%20Housing");
  await expect(
    page
      .getByRole("navigation", { name: "Applicant tabs" })
      .getByRole("button"),
  ).toHaveCount(3);
  await page
    .getByRole("spinbutton", { name: "Household members", exact: true })
    .fill("4");
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await page
    .getByRole("combobox", { name: "Housing situation", exact: true })
    .selectOption("unclear");
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await page
    .getByRole("checkbox", { name: "Housing evidence available", exact: true })
    .uncheck();
  await expect(
    page.getByText(/Documentation completeness: 66.7/),
  ).toBeVisible();
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await page
    .getByRole("checkbox", {
      name: "Information needs clarification",
      exact: true,
    })
    .check();
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await page
    .getByRole("checkbox", {
      name: "I confirm all values are synthetic.",
      exact: true,
    })
    .check();
  await page
    .getByRole("button", { name: "Submit application", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Your application" }),
  ).toBeVisible();
  const id = await page.locator(".reference").innerText();
  let record = await (await request.get(`/api/applications/${id}`)).json();
  expect(record.status).toBe("unassessed");
  expect(record.assessment).toBeUndefined();
  await page
    .getByRole("button", { name: "Switch to administrator", exact: true })
    .click();
  await expect(
    page
      .getByRole("navigation", { name: "Administrator tabs" })
      .getByRole("button"),
  ).toHaveCount(5);
  await page
    .getByRole("textbox", { name: "Search cases", exact: true })
    .fill(id);
  await page.getByRole("button", { name: `Open ${id}`, exact: true }).click();
  await page
    .getByRole("button", { name: "Open AI assessment", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Run AI Assessment", exact: true })
    .click();
  await expect(
    page.getByRole("img", {
      name: "Actual SHAP feature contributions; numeric values follow in the input summary",
    }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Continue to human review", exact: true })
    .click();
  await page
    .getByRole("combobox", { name: "Review action", exact: true })
    .selectOption("request_evidence");
  await page
    .getByRole("textbox", {
      name: "Reviewer notes & mandatory reason",
      exact: true,
    })
    .fill("Please clarify the missing current housing evidence for this demo.");
  await page
    .getByRole("button", { name: "Record review action", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Confirm review action", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Switch to applicant", exact: true })
    .click();
  await page.reload();
  await expect(
    page.getByText("A caseworker has requested more information", {
      exact: true,
    }),
  ).toBeVisible();
  record = await (await request.get(`/api/applications/${id}`)).json();
  expect(record.status).toBe("pending");
  await page
    .getByRole("button", { name: "Switch to administrator", exact: true })
    .click();
  await page.getByRole("button", { name: "Human Review", exact: true }).click();
  await page
    .getByRole("combobox", { name: "Review action", exact: true })
    .selectOption("routine");
  await page
    .getByRole("textbox", {
      name: "Reviewer notes & mandatory reason",
      exact: true,
    })
    .fill("Administrative intake review completed; no housing decision.");
  await page
    .getByRole("button", { name: "Record review action", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Confirm review action", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Switch to applicant", exact: true })
    .click();
  await page.reload();
  await expect(
    page.getByText(
      "Your administrative review is complete. This is not a housing approval or allocation.",
      { exact: true },
    ),
  ).toBeVisible();
  record = await (await request.get(`/api/applications/${id}`)).json();
  expect(record.status).toBe("resolved");
  expect(record.history).toHaveLength(4);
  expect(record.assessment.model_version).toBe("rf-1.0");
  expect(Number.isNaN(Date.parse(record.assessment.assessed_at))).toBe(false);
  const explanation = await (await request.get(`/api/applications/${id}/explanation`)).json();
  expect(explanation.score).toBeCloseTo(record.assessment.score, 12);
  expect(explanation.additivity_error).toBeLessThan(1e-6);
  await page.getByRole("button", {name:"Start another application",exact:true}).click();
  for (let step = 0; step < 4; step++)
    await page.getByRole("button", {name:"Continue",exact:true}).click();
  await page.getByRole("checkbox", {name:"I confirm all values are synthetic.",exact:true}).check();
  await page.getByRole("button", {name:"Submit application",exact:true}).click();
  await expect(page.locator(".session-application")).toHaveCount(2);
  await page.reload();
  await expect(page.locator(".session-application")).toHaveCount(2);
  await page.getByRole("button", {name:id,exact:true}).click();
  await expect(page.getByText("Your administrative review is complete. This is not a housing approval or allocation.",{exact:true})).toBeVisible();
});

test("Merged audit and real sandbox comparisons", async ({ page, request }) => {
  await page.goto("/#admin/Fairness%20%26%20Sandbox");
  await page
    .getByRole("button", { name: "Run group analysis", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Rerun 200 paired comparisons", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Run comparison", exact: true })
    .click();
  await expect(
    page.getByText("Changed synthetic audit group from Audit A to Audit B.", {
      exact: true,
    }),
  ).toBeVisible();
  const source = await (await request.get("/api/applications/HAB-0023")).json();
  await page
    .getByRole("combobox", { name: "Sandbox input", exact: true })
    .selectOption("conflicting_information");
  await page
    .getByRole("button", { name: "Run comparison", exact: true })
    .click();
  await expect(
    page.getByText("Changed conflicting information from 0 to 1.", {
      exact: true,
    }),
  ).toBeVisible();
  const changed = await (
    await request.get("/api/applications/HAB-0023")
  ).json();
  expect(changed).toEqual(source);
  await page.screenshot({
    path: "../docs/screenshots/v6-runner-sandbox.png",
    fullPage: true,
  });
});

test("CSV and saved reports available", async ({ request }) => {
  const csv = await request.get("/api/dataset/download");
  expect(csv.ok()).toBeTruthy();
  expect((await csv.text()).trim().split("\n")).toHaveLength(2001);
  const metrics = await (await request.get("/api/model/metrics")).json();
  expect(metrics.confusion_matrix).toEqual([
    [163, 41],
    [26, 70],
  ]);
});
for (const width of [375, 768, 1280])
  test(`Viewport ${width}, full labels and accessibility`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/#admin/Overview");
    await expect(
      page.getByText("Total submitted applications", { exact: true }),
    ).toBeVisible();
    const buttons = page
      .getByRole("navigation", { name: "Administrator tabs" })
      .getByRole("button");
    expect(await buttons.allTextContents()).toEqual([
      "Overview",
      "Applications",
      "AI Assessment",
      "Fairness & Sandbox",
      "Human Review",
    ]);
    expect(
      await page.evaluate(
        () =>
          document.documentElement.scrollWidth <=
          document.documentElement.clientWidth,
      ),
    ).toBeTruthy();
    await page.getByRole("link", { name: "Skip to main content" }).focus();
    await page.keyboard.press("Enter");
    await expect(
      page.getByRole("heading", { name: "Overview", exact: true }),
    ).toBeVisible();
    const accessibility = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa"])
      .analyze();
    expect(accessibility.violations).toEqual([]);
    await page.screenshot({
      path: `../docs/screenshots/v6-runner-${width}.png`,
      fullPage: true,
    });
  });
