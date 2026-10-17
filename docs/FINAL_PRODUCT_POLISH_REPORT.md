# Final terminology cleanup and workflow verification

18 October 2026 · Advaith-Ganesh/HABITAT · Branch: `habitat-final-polish`.

## Changes and retained boundaries

- Professional wording replaces development-stage descriptions in the applicant introduction, shared banner/footer, administrator captions, intake-reference panel, API document summary/policy responses, primary README and product walkthrough. [Every before/after replacement](final-polish-wording.json).
- New submissions receive `HAB-XXXXXXXX` references (eight uppercase hexadecimal characters). Existing `DEMO-` references, seed identifiers, policy-pack IDs/paths and immutable historical records remain compatible; no database was reset or deleted. Historical screenshots and saved evidence are retained as recorded.
- **Sandbox · Synthetic Data** remains visible. Help explicitly explains the original, reproducible, public 2,000-record dataset, genuinely trained Random Forest, generated-scenario evaluation, absence of actual housing decisions, and unimplemented production authentication and real-world validation. Project-defined intake prompts are explicitly **not statutory rules**.
- No CSS, visual-design assets, model, dataset, SHAP implementation or model metrics changed. Team credits, charts, existing screenshots, architecture and setup instructions remain. README validation now checks links/artifacts without incorrectly requiring every future application change to be documentation-only; historical showcase evidence is preserved.

## Genuine workflow result — PASS

A fresh application was completed and submitted in the real browser as **`HAB-17F6A5CE`**: household3, income£1,750, stable housing, missing income evidence, declared information completeness82. It was confirmed directly in SQLite and found by exact reference in the administrator portal. The saved Random Forest returned **0.4158352705939491 (41.6%)**, with genuine SHAP reconciling to the score (additivity error **5.384581669432009e-15**). A caseworker requested evidence with the saved reason:

> Please clarify the missing income evidence in this synthetic housing application.

The applicant saw **Additional information requested**. Reloading both portals and fully stopping/restarting the backend preserved the application, assessment and all three history events. A separate real API retry probe using the same synthetic payload and a stable key created **`HAB-EF7F4906`** once: three identical replays before restart and three after restart returned that reference, with one submitted event and no duplicate record. The CI browser suite additionally verifies lost-success-response recovery on the same browser submission.

[Machine-readable evidence and preserved hashes](../reports/final-polish-verification.json) · [Assessment screenshot](screenshots/final-polish-assessment.png) · [Applicant after restart](screenshots/final-polish-applicant.png) · [Saved review history](screenshots/final-polish-history.png) · [Disclosures](screenshots/final-polish-transparency.png).

The historical database remains13 applications/27 events; the default sandbox remains12/24. The browser workspace grew from14/29 to16/33 solely through the fresh application and retry probe. Every original row in all three databases remains unchanged. All162 protected original model/data/evaluation/chart/brand files retain their SHA-256s.

## Verification

| Check | Result |
|---|---|
| Python suite | **PASS:111 tests**,15 dependency deprecation warnings |
| ESLint / TypeScript / production build | **PASS** |
| Existing README validator | **PASS:58 exact-case links/assets;5 shell examples parsed**; historical result preserved |
| Extended README validation | **PASS:**links/fragments,7 safe SVGs,10 canonical protected artifact hashes; [result](final-polish-readme-validation.json) |
| Real browser → API → SQLite → model/SHAP → human review → applicant → restart | **PASS**, as described above; no simulated success responses |
| Supported Linux Playwright / GitHub Actions | **PASS:9 Playwright tests,0 skipped**, including the full applicant/admin journey, identical retries and 375/768/1280 accessibility matrix. [Successful source CI](https://github.com/Advaith-Ganesh/HABITAT/actions/runs/39080435230), source commit `bb1f12e` |

The CI run also passed clean dependency installation,111 Python tests, lint, TypeScript and production build. The final evidence-only follow-up changes this report and verification records; application code remains identical to the verified source. Merge is performed only after the pull-request checks succeed.

## Remaining limitations

The retained validation routing-recall target still **FAILS:84.69% versus90%**. Subgroup disparities remain. Real-world housing validation, production auth/RBAC/tenant isolation and full accessibility certification remain **NOT TESTED / not implemented**. The previously documented restricted-macOS standalone Chromium launch failure is unchanged; supported Linux CI and real local in-app browser verification are reported separately. Historical IDs, assessment text and audit history are not rewritten to hide their provenance. This is final product polish, not production housing readiness.
