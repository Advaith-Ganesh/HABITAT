# HABITAT AI — final applicant–administrator integration audit

**17 October 2026 · V6 · checkpoint `09906a1` · branch `habitat-v6-integration`**

**Core synthetic workflow: PASS.** Two real browser submissions reached the same SQLite-backed administrator portal; saved Random Forest inference and SHAP worked; reasoned human actions reached applicant tracking and survived reload and a backend process restart. No critical defect was observed in that tested workflow. This is a local synthetic demonstration, not an operational housing service. The standalone browser suite is **not green**.

## Executed results

| Check | Status | Evidence |
|---|---|---|
| Backend/API full suite | PASS | [101 passed, 15 dependency deprecation warnings](../reports/v6-pytest.txt) |
| Frontend ESLint / TypeScript / production build | PASS | [Lint](../reports/v6-lint.txt), [types](../reports/v6-typecheck.txt), [build](../reports/v6-frontend-build.txt) |
| Real-browser applicant → administrator → RF → SHAP → human → applicant | PASS | [CUA observations](../reports/v6-live-browser.json), [assessment screenshot](screenshots/v6-assessment.png), [SHAP](screenshots/v6-explanation.png), [completed applicant](screenshots/v6-applicant-completed.png) |
| Multiple applications and cross-tab refetch | PASS | DEMO-41a21175 and DEMO-cd4ec01f in the same server-backed session; administrator totals 14→15 and unassessed 1→2 on the second submission |
| Invalid inputs / missing fields | PASS | Native browser blocks household 0; API rejects each of all 15 missing intake fields and invalid values without saving; test_v6_integration.py |
| Real inference / SHAP / repeated assessment | PASS | API score exactly matches loaded model; additivity error 5.440092820663267e-15; reassessment saves a new timestamp; resolved cases reject reassessment with 409 |
| Human request / completion / escalation / override | PASS | Real browser request and completion; API tests exercise all four outcomes, mandatory reasons, timestamps and append-only history |
| Refresh and actual backend process restart | PASS | Stop/restart Uvicorn against the same v6-browser.db; both session associations, two assessments and two review actions remain; [integrity evidence](../reports/v6-integrity.json) |
| Backend unavailable and recovery | PASS | Backend stopped, Refresh status displays Service unavailable, backend restarted, Retry recovers; [actual outage screenshot](screenshots/v6-backend-unavailable.png) |
| Fairlearn, paired suite and sensitivity controls | PASS | Real browser recomputes group analysis and 200 pairs; [read-only model audit](../reports/v6-ml-audit.json) matches preserved reports |
| CSV download and all GET endpoints | PASS | 2,000 rows + header, SHA matches original; 19 endpoint checks returned 200; [endpoint evidence](../reports/v6-endpoints.json) |
| Original data/model/reports/source preservation | PASS | All 10 evaluation inputs byte-identical to checkpoint; original SQLite 13 applications/27 events untouched; checkpoint paths retained |
| Standalone Playwright suite | FAIL | [1 request-only test passes; 5 browser cases fail before assertions at Chrome launch](../reports/v6-e2e-output.txt); [machine report](../reports/v6-e2e.json) |
| Standalone 375/768/1280 viewport matrix and axe | NOT TESTED | Chrome launch limitation; real in-app 1280px view inspected with no horizontal overflow |
| Validation routing-recall target ≥90% | FAIL | Preserved configuration achieves 84.7% validation recall; no test-set tuning/retraining |
| Universal fairness / real-world usefulness | NOT TESTED | Synthetic labels; subgroup concerns persist; no universal fairness claim |
| Fresh installation, deployment, production security and full WCAG review | NOT TESTED | Existing pinned environment used; no production authentication/RBAC implemented |

## Concrete integration changes

Applicant navigation is **Apply for Housing / My Applications / Help & Transparency**. Administrator navigation retains exactly five full labels with icons. The local portal switch explicitly does not provide access control. The small disclosure reads **Sandbox · Synthetic Data**. Repetitive record/form demo labels were reduced; historical event notes and honest synthetic-policy explanations remain intact.

Submitted records are stored in `applications`, actions in append-only `events`, and a new additive `applicant_session_applications` table associates references with an anonymous sandbox UUID. `create_all` creates this table for existing databases without replacing application or event rows. Browser localStorage holds only a grouping key, selected references, theme and optional draft; it is not the submission database. Clearing browser storage loses the session key, not SQLite records; saved references can be loaded manually. This grouping is not authorization: the local API remains intentionally unauthenticated.

`Submission` requires every structured intake field and validates ranges, finite numbers and document-count consistency. Defaults remain in the reusable historical/internal `Case` schema. No new personal data is collected. Submission, list, dashboard, assessment and review all use the same FastAPI/SQLite service. Mutation notifications, visibility refetch and Refresh controls update views without fixed-interval API polling.

**Run AI Assessment** calls the saved Pipeline. The stored assessment includes `model_version`, `model_sha256`, prediction and UTC `assessed_at`. Repeated inference is deterministic and adds a timestamped history event. Human follow-up remains pending until explicitly completed; completed cases cannot be reopened by reassessment. Document completeness is declared present / three actual requirements ×100 and is displayed separately from model-estimated additional-review probability.

## Working routes

| Operation | Route |
|---|---|
| Submit structured application | `POST /api/applications` (201; invalid/missing 422) |
| List this sandbox session | `GET /api/applicant/applications`, header `X-Sandbox-Session: <UUID>` |
| Administrator list / detail / actual totals | `GET /api/applications`, `/api/applications/{aid}`, `/api/dashboard` |
| Run saved model / real SHAP | `POST /api/applications/{aid}/assess`, `GET /api/applications/{aid}/explanation` |
| Queue / timestamped reasoned human action | `GET /api/reviews`, `POST /api/reviews/{aid}/resolve` |
| Held-out performance and model provenance | `GET /api/model/metrics`, `/api/model/baseline`, `/api/model/metadata`, `/api/model/safeguard` |
| Fairlearn / paired fairness / sensitivity | `POST /api/fairness/run`, `/api/fairness/counterfactual`, `/api/sandbox/compare` |
| Dataset | `GET /api/dataset/download`, `/metadata`, `/card`, `/dictionary` |
| Health and schema | `GET /health`, `/docs`, `/openapi.json` |

The three applicant hash routes and five administrator hash routes all resolve through the same React application. Cross-origin development requests permit the sandbox-session header. Missing session headers are 422 for the session list; legacy complete API submissions without a session remain supported.

## Actual model, SHAP and fairness results

The preserved fitted RandomForestClassifier has **180 trees**, depth 8, leaf minimum 8, balanced weights, seed 42 and nine allowed inputs. Training/validation/test remain **1,400/300/300** within the **2,000-record source**. Separate paired fairness scenarios contain **400 records / 200 pairs**. Source generation reproduces bytes with pinned dependencies; related scenario families never cross partitions, and application/scenario intersections are zero. Preprocessing fits training only. No retraining occurred.

| Held-out test metric | Actual result |
|---|---:|
| Accuracy | 77.6667% |
| Precision | 63.0631% |
| Recall | 72.9167% |
| F1 | 67.6329% |
| ROC-AUC | 0.81929126 |
| Confusion matrix | [[163,41],[26,70]] |

The browser case used household 4, income £1800, Stable housing, one missing income-evidence declaration, no conflict or specialist request. Actual inference: **0.530595215028465** additional-review probability. Documents: **2/3 =66.6667%**. Tree SHAP uses the positive-class output of the same saved model; base + all signed contributions reconciles with stored probability within **5.44e-15**. The frontend displays actual input values and contributions, with explicit unavailable/loading states instead of fabricated explanations. Missing-model/input and SHAP-failure behavior are covered by backend tests using controlled failures; no production artifact was removed.

Fairlearn sample sizes are A **130**, B **102**, C **68**. FNRs are **34.1463%, 9.3750%, 39.1304%**; the maximum gap is **29.7554 percentage points**. B/C retain potential-concern flags. The 200 excluded-audit-label pairs have zero changed classifications and zero score differences by construction. This does not establish absence of proxy bias. A real model-input comparison (HAB-0023 conflict 0→1) changes **14.9%→65.1%**, with new SHAP calculations and no saved-case write.

With uncertainty escalation, held-out human-routing workload rises 37.0%→57.3%; errors among remaining routine cases change 26/189→12/128. These are different simulated populations, not causal service improvements. The validation target miss and subgroup disparities remain visible.

## Actual persistence and data provenance

Browser work used `$PROJECT_ROOT/.test-runtime/v6-browser.db`, cloned from the original DB. The original `habitat.db` remains at **13 applications and 27 events** and matches its pre-V6 backup row for row. No test submissions were inserted into it.

The new browser references are `DEMO-41a21175` (completed) and `DEMO-cd4ec01f` (unassessed). The first has five durable events: submission, assessment, reassessment, information request and completion. The applicant session list still contains both after browser reopen/reload and full backend stop/start. Final clone totals: **15 applications, 1 unassessed, 5 pending, 2 completed, 0 open information requests**. These are observed clone values, never hard-coded UI counters.

Model SHA-256: `bd4add37db3308b56a51410d215b4012b37384b84a450f137ccfabb1e8174655`.

Public source SHA-256: `196d2f715cbc959dac5c27e77d3db2edd31b6cafab1a0a296a9f445a8444f255`.

The existing [number/source audit](DATA_VALUE_AUDIT_V5.md) still applies; new session counts come from an actual SQL query and assessment dates from stored UTC timestamps. Active screen/code review found no fabricated product/evaluation statistics or disconnected core controls. Business prices/costs remain explicitly labelled assumptions. Exercised controls include all portal tabs, search/open, form validation and progression, save/restore/reset draft, reference lookup/selection, assessment/reassessment, mandatory-reason review confirmation, refresh/retry, theme switching, fairness reruns and both comparison types. This is bounded verification, not a claim that every input/visual/accessibility permutation was tested.

## Remaining defects and limits

- Standalone Chrome exits with SIGABRT during launch; five browser tests cannot execute here. The real in-app browser did execute the workflow. No sandbox bypass was attempted.
- The 90% validation recall target is missed and subgroup disparities remain. Preserving the existing model was explicit; no threshold or test-data manipulation conceals the result.
- No production auth/RBAC, reviewer identity assurance, uploads, actual allocation decisions, real-world outcome labels, calibration or security certification. Keep loopback-only and use synthetic inputs.
- No server idempotency key: inspect an uncertain submission before retrying. A lost browser session key requires saved references.
- Exact mobile matrix, axe/full WCAG, fresh install and deployment are not tested. Normal backend suite emits 15 dependency deprecation warnings.
- Team names and genuine video link still require human-supplied credits; no names, usage figures or testimonials were invented.

## Exact startup and verification commands

From the repository root, using the existing pinned Python environment and installed frontend dependencies:

```bash
# Terminal 1: default persisted workspace
bash scripts/start_backend.sh
# Terminal 2: both portals in one frontend
bash scripts/start_frontend.sh
```

Open `http://127.0.0.1:5173`. Both portals use port 8000. For the browser evidence database used in this audit, instead start the backend with:

```bash
HABITAT_DATABASE_URL=sqlite:///./.test-runtime/v6-browser.db MPLCONFIGDIR=./.test-runtime/matplotlib .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

That private test database is not shipped or committed. A fresh default workspace is initialized automatically. Installation commands and the full architecture/methodology are in [README](../README.md).

```bash
MPLCONFIGDIR=/tmp/habitat-matplotlib .venv/bin/python -m pytest -q
MPLCONFIGDIR=/tmp/habitat-matplotlib .venv/bin/python -m scripts.audit_v6
.venv/bin/python -m scripts.validate_readme_v6
cd frontend
npm run lint
npm run typecheck
npm run build
npm run test:e2e
```

The last command currently exits nonzero for the documented browser-launch failures. Do not represent it as passed. See [demonstration instructions](DEMO_CHECKLIST.md) and [submission status](SUBMISSION_READINESS.md).

## Exact V6 files modified or added

The following inventory includes source, tests, documentation and evidence relative to the checkpoint. Generated production assets are included in the ZIP but ignored by Git; installed dependencies, database files, caches and raw browser traces are excluded.

- `README.md`
- `backend/main.py`
- `docs/DEMO_CHECKLIST.md`
- `docs/FINAL_INTEGRATION_AUDIT.md`
- `docs/SUBMISSION_READINESS.md`
- `docs/screenshots/v6-applicant-completed.png`
- `docs/screenshots/v6-applicant-request.png`
- `docs/screenshots/v6-assessment.png`
- `docs/screenshots/v6-backend-unavailable.png`
- `docs/screenshots/v6-explanation.png`
- `docs/screenshots/v6-fairness.png`
- `docs/screenshots/v6-landing.png`
- `docs/screenshots/v6-overview-dark.png`
- `docs/screenshots/v6-overview.png`
- `frontend/e2e/habitat.spec.ts`
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/playwright.config.ts`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/NewCaseForm.tsx`
- `frontend/src/components/ReviewWorkspace.tsx`
- `frontend/src/components/ui.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/main.tsx`
- `frontend/src/style.css`
- `reports/v6-changed-files.txt`
- `reports/v6-e2e-output.txt`
- `reports/v6-e2e.json`
- `reports/v6-endpoints.json`
- `reports/v6-file-manifest.json`
- `reports/v6-frontend-build.txt`
- `reports/v6-integrity.json`
- `reports/v6-lint.txt`
- `reports/v6-live-browser.json`
- `reports/v6-ml-audit-output.txt`
- `reports/v6-ml-audit.json`
- `reports/v6-pytest.txt`
- `reports/v6-readme-validation-output.txt`
- `reports/v6-readme-validation.json`
- `reports/v6-safeguard.json`
- `reports/v6-typecheck.txt`
- `scripts/audit_v6.py`
- `scripts/validate_readme_v6.py`
- `tests/test_v6_integration.py`
