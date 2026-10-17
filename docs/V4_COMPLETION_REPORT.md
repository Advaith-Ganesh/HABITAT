# HABITAT AI V4 completion audit — 17 October 2026

**PASS: the tested local applicant-to-administrator-to-applicant journey works. Ready for this synthetic demonstration only.** No authentication, role-based access or production housing deployment is claimed.

## 1. Files and architecture

Worked in the existing repository; checkpoint `7da5c66`, branch `habitat-v4-portals`. React/Vite, FastAPI, SQLite, sklearn, Tree SHAP and Fairlearn retained. No retraining. `reports/v4-changed-files.txt` lists final changes. Principal changes: main.tsx, AppShell, NewCaseForm, new ReviewWorkspace components, shared history, responsive styles, backend response/metrics/sandbox endpoints, ml/safeguard.py, versioned audit script, new workflow tests, V4 browser suite, SVG logo/favicon and documentation. Historical source paths remain; old pages are removed from active navigation and merged into the five-tab workflow.

## 2–3. Interface and applicant portal

PASS: original square home/H-monogram SVG, reusable logo and favicon. Navy/off-white/teal design, Inter, dark/light themes. Full sidebar labels with icons; no icon-only desktop collapse. Applicant navigation exactly Apply for Housing, My Application, Help & Transparency. Anonymous demo session remembers a reference. Form saves actual declarations, submits without assessment and exposes the saved reference/status. Requests and completion persist and are visible to the applicant. No personal document upload or government submission exists.

## 4. Administrator portal

PASS: exactly Overview, Applications, AI Assessment, Fairness & Sandbox, Human Review. Actual overview counts: submitted, unassessed, pending and latest unresolved information requests. Search/filter/pagination/detail view, real assessment and explanations, merged diagnostics/sandbox, mandatory-reason human actions. Business assumptions are an expandable Overview section rather than another tab.

## 5–7. Dataset, model and fairness

PASS: 2000 public records, 1400/300/300 related-family-isolated splits, byte-reproducible generator, trained 180-tree Random Forest and preprocessing, exact saved-model predictions, SHAP additivity, independently recomputed evaluation/Fairlearn and separate 200-pair fixture. All nine protected model/config/CSV/split/evaluation/fairness hashes unchanged; original database still matches backup (13 apps/27 events). No source path from the safety checkpoint was deleted.

Actual test results: accuracy77.67%, precision63.06%, recall72.92%, F1 67.63%, ROC-AUC0.8193, matrix[[163,41],[26,70]], n300. Checklist recall91.67% exceeds model recall. Desired validation routing recall90%: **FAIL**, actual84.69%.

Audit A n130 FPR17.98% FNR34.15%; B n102 FPR22.86% FNR9.38%; C n68 FPR20.00% FNR39.13%. FNR equality: **FAIL**, gap29.76pp. Group audit calculations: **PASS**. These are descriptive synthetic findings. Paired invariance: **PASS** for its limited excluded-attribute comparison, not universal fairness. No mitigation claimed.

## 8. Document completeness

PASS: income/identity/current-housing declarations are the three actual demo requirements. Present/3×100; all eight combinations tested. UI uses actual saved flags and names missing categories. Browser case had two present, one missing:66.7%. This is separate from its81.1% additional-review model probability. Historic intake-completeness inputs remain untouched; new form derives that existing model input from document declarations. Real-world validity of this mapping is NOT TESTED.

## 9. Working sandbox and safeguard

PASS: changing only audit group gives identical actual model/SHAP outputs; changing the genuine conflict input on HAB-0023 from0→1 gives14.9%→65.1% and changed attributions. Database snapshot comparison proves no saved case mutation. Same-value selections explicitly say no input changed. Invalid fields/values return422.

PASS: no-uncertainty baseline routes111/300(37%) to humans, leaving26 errors/189 routine-route cases(13.76%). Existing validation-selected margin0.16 routes172/300(57.33%) to humans, leaving12/128(9.375%). Difference: +20.33pp workload and −4.38pp remaining-route error. Different remaining populations; no causal benefit or real cost-saving claim. No test-set threshold tuning.

## 10. Tests and actual browser evidence

| Result | Check | Evidence |
|---|---|---|
| PASS | Full backend/API suite | 72 passed; 15 dependency warnings; v4-pytest.txt |
| PASS | Frontend lint/types/build | Zero lint warnings, tsc, Vite build; versioned logs |
| PASS | Real browser full journey | DEMO-92ed2c03, submitted→unassessed→81.1% assessment→real SHAP→request→applicant sees reason→routine completion→applicant sees completed after reload |
| PASS | Request/queue semantics and history | Requests remain pending, routine completion resolves, both timestamped reasons persist |
| PASS | Sandbox, group and paired reruns | Real model outputs; no case/artifact writes |
| PASS | V4 register controls | Two disjoint six-row pages, five pending records, exact-reference search |
| PASS | Live rendering and navigation | Observed986px viewport, no page overflow, exactly five admin and three applicant labels |
| PASS | Standalone request-only test | CSV2000 rows and genuine model matrix returned |
| FAIL | Standalone browser runner | Five cases failed at Chromium launch before assertions; not application assertion failures |
| NOT TESTED | Exact375/768/1280 matrix and axe | Browser launch restrictions; do not claim responsive/accessibility certification |
| NOT TESTED | Production role/security, expert housing validity | Out of sandbox scope; necessary before real use |

Genuine captures: docs/screenshots/v4-applicant-form.png, v4-applicant-submitted.png, v4-assessment.png, v4-applicant-request.png, v4-applicant-completed.png, v4-sandbox.png and v4-overview.png. Live browser records in v4-live-browser.json; integrity, safeguard and ML evidence in reports/v4-*.json.

## 11. Problems repaired and remaining limits

Submission is now separate from inference. Document completeness is computed from requirements rather than user-entered percentage. Recent event text no longer mislabels assessed events as submissions. Skip-to-content preserves the portal route. Loading tables and unavailable health have explicit states. Form review uses plain labels/yes-no and rounded percentage. Sandbox distinguishes audit invariance from legitimate-feature sensitivity and cannot silently save changes. Old database rows and model/report bytes remain preserved.

The model is still a synthetic benchmark with missed validation target and group disparities. No calibration, confidence intervals, expert real housing outcomes, authentication/RBAC, tenant isolation or reviewer identity verification. Append-only triggers do not constrain an administrator. References are openly loadable in this local demo. No applicant evidence-upload/response workflow is built; users can view requests only. Browser storage failure requires keeping a reference manually. A timed-out submission should be checked before retrying; no server idempotency key is implemented. Production and exact mobile/axe readiness are NOT TESTED.

## 12. Startup

From the project root in separate terminals: `bash scripts/start_backend.sh` and `bash scripts/start_frontend.sh`. See README for fresh dependency installation/build. Open http://127.0.0.1:5173. Verification servers use a test database clone; canonical startup uses the original local demo DB. No GPT/API key is required. Do not run reproduce.sh merely to start the app; it intentionally retrains.
