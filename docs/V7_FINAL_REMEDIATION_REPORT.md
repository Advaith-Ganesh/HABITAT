# HABITAT AI — V7 independent audit remediation

Audited baseline: `7fdc928d9c23a14d7222c0797a2cbb304f0d8982`. Work stays in **Advaith-Ganesh/HABITAT**. The existing product, original visual identity, saved Random Forest and all ten canonical model/data/evaluation inputs were preserved. No retraining or test-based policy selection occurred.

**Final-source verification: PASS for the tested synthetic workflow; unresolved model/production limits remain below.** Earlier Linux run [39075258803](https://github.com/Advaith-Ganesh/HABITAT/actions/runs/39075258803) passed all nine browser tests. Stronger full-form recovery assertions subsequently caught an additional controlled-field bug, which was corrected and rerun. Only the final-source result below determines the final verification status; earlier green results are not substituted for it.

## Results by audit priority

| Issue | Root cause and change | Test and evidence | Status | Remaining limitation |
|---|---|---|---|---|
| 1. Standalone Playwright | V6 hard-coded system Chrome. Installed version-matched managed Chromium; one absolute project browser-cache path now serves install and test. Linux CI builds before backend entrypoint tests. | Full nine-case suite; [local OS errors](../reports/v7-e2e-local-output.txt), [Linux evidence](../reports/v7-ci-final-evidence.json), [workflow](../.github/workflows/verification.yml). | PASS Linux; FAIL restricted macOS launch | macOS sandbox still denies Mach-port registration before browser assertions. No tests disabled or launch-security bypass added. |
| 2. Missed recall target | Original margin search stopped at0.16. Validation-only frontier expanded to every observed score cutoff; no cutoff meets both90% recall and a predeclared provisional70% extra-review ceiling. Original policy retained. | [Reproducible selection code](../ml/validation_policy.py), [frozen investigation](../reports/v7-validation-policy-investigation.json). Candidate was not tested on final test. | PASS investigation; FAIL active90% target | Ceiling is an operating assumption, not validated buyer capacity. A larger review budget could support90.8% validation recall at73.7% extra-review routing. |
| 3. Fairness gaps | Small noisy synthetic subgroups have differing errors/case mix. Added counts, label balance, uncertainty/routing by group and descriptive case characteristics; exact proxy warning visible. | [Investigation](../reports/v7-fairness-input-investigation.json); real browser Fairlearn/pair reruns and CI audit screens. | PASS investigation and warnings | Disparities remain; no causal explanation, universal fairness or real-world fairness established. |
| 4. Training/inference consistency | V6 mapped document availability into a different, noisy continuous training feature. V7 separately declares information completeness; document percentage still comes only from three evidence flags. Training-only numeric/category/imputation checks now force human handling when flagged. | [Input checks](../ml/input_audit.py), imputer/order assertions, real inference + reconciled SHAP, OOD UI tests. | PASS implemented checks | Separate declaration is not a validated real-world measurement protocol. Range/category checks cannot detect all shift or novel combinations. |
| 5. Demonstration records | Startup previously read12 test-split rows. Fresh/default sandbox now uses12 hand-authored, outcome-free UI cases; none duplicate benchmark/pair feature rows. Historical DB retained. | [UI fixture](../data/demo/applications.json), no-overlap test, [reset](../scripts/reset_sandbox.py), actual backup/reset verification. | PASS | Existing custom/legacy databases are not silently rewritten. Reset requires backend stopped and backs up before replacement. |
| 6. Submission retries | No request identity existed. UUID retry key + normalized payload hash + serialized SQLite transaction now prevent repeated/concurrent inserts. Pending browser payload/key survives reload until success. | Eight concurrent retries create one record; conflicting payload409; invalid data reserves nothing; storage rollback/retry; lost-success-response browser test; actual process-restart replay. | PASS | Missing keys remain supported for legacy callers. Clearing/unavailable browser storage can lose reload recovery; changing payload creates a new operation. |
| 7. Security boundaries | Local sandbox has no authentication/RBAC and references/session IDs are not credentials. Retained explicit disclosures; loopback scripts, restricted CORS, TrustedHost checks and0600 DB files verified. | Local binding inspection, CORS/Host/schema/permission tests; [integrity evidence](../reports/v7-integrity.json). | PASS bounded audit | Admin actions and record access remain unauthenticated to local clients; no encryption, tenant isolation or adversarial audit. Never expose publicly. |
| 8. Responsive/accessibility | Legacy mobile drawer CSS hid navigation; audit scrollers lacked keyboard focus. A V7 validation-message handler cleared state during input capture and could reset corrected numeric values. Completed mobile progress controls also lost accessible names when their visible text collapsed. Fixed visibility, visible mobile nav grid, labelled focusable table regions,44px controls, accessible errors, bubbling change handling and explicit progress-control names. | 375/768/1280 navigation-in-viewport, actual form progression/recovery, skip-link focus, table keyboard focus, no body overflow and axe checks;22 token-contrast checks. | PASS tested Chromium matrix | Automated Chromium/axe and sampled contrast are bounded checks; physical touch devices, screen readers, Safari/Firefox and full WCAG review not tested. |
| 9. Business/judging evidence | Broad claims needed a specific buyer/user and grounded hypotheses. README/pitch now identify intake caseworkers, proposed authority/association buyers, public problem sources, shadow pilot and second-customer plan. Cost illustration includes human time for every case. | [Pitch mapped to supplied20/20/25/20/15 rubric](PITCH_V7.md), README source links and arithmetic. | PASS documentation | No customers, sales, measured savings, external model validation or pilot results invented. |
| 10. README | Long audit detail obscured product overview. Retained original logo/brand; added concise value proposition, actual V7 screenshot, one architecture diagram, features/results/demo links and linked detailed evidence below. | Exact-case local links/images and shell syntax validation; startup/build/test commands separately executed. | PASS | Team names/video link still need genuine human-supplied content. Remote-link uptime not monitored. |
| 11. Final checks | Combined code, ML, browser, persistence and provenance verification rather than file-existence claims. | [Local111-test suite](../reports/v7-pytest.txt), lint/types/build, read-only audit,20 GET endpoints, genuine screenshots, Linux CI. | PASS tested synthetic workflow | See explicit FAIL and NOT TESTED boundaries below. |

## Exact final execution results

Verified source commit: **`bcc1833a9a9e5e772f7d4098441299cd5457a894`**. [Final source CI run39076409671](https://github.com/Advaith-Ganesh/HABITAT/actions/runs/39076409671) completed successfully. Later publication changes contain evidence/documentation only;76 source files match that green commit byte-for-byte. [Source comparison](../reports/v7-source-verification.json).

| Executed check | Genuine result | Evidence |
|---|---|---|
| Python suite, local and clean Linux installation | **111 passed**,15 dependency warnings | [Local output](../reports/v7-pytest.txt), [final CI log](../reports/v7-ci-final-log.txt) |
| ESLint / TypeScript / production build | **PASS**, local and Linux | [lint](../reports/v7-lint.txt), [types](../reports/v7-typecheck.txt), [build](../reports/v7-frontend-build.txt) |
| Complete Playwright suite on Linux | **9 passed,0 failed,0 skipped**,38.4s | [Machine report](../reports/v7-e2e-linux.json), [artifact provenance](../reports/v7-ci-final-evidence.json) |
| 375/768/1280, all8 portal pages, full form/error recovery, nav visibility/44px height, focus, table keyboard access, overflow and axe | **PASS** within this Chromium scope | [375 overview](screenshots/v7-runner-375.png), [375 form](screenshots/v7-runner-applicant-375.png), [768 audit](screenshots/v7-runner-fairness-768.png), full CI screenshots |
| Selected light/dark token contrast | **22 passed** | [Contrast output](../reports/v7-contrast-output.txt) |
| Real saved-model load/inference/SHAP/Fairlearn; source/split/reproducibility/isolation | **PASS**, no retraining | [Read-only ML audit](../reports/v7-ml-audit.json), [input/fairness investigation](../reports/v7-fairness-input-investigation.json) |
| HTTP endpoints / dataset download | **20 GET endpoints returned200**,2,000 CSV rows + header, original SHA matches | [Endpoint list](../reports/v7-endpoints.json), [integrity](../reports/v7-integrity.json) |
| Idempotency, actual backend restart, outage/recovery, independent reset/backup, original DB preservation | **PASS** | [restart replay](../reports/v7-restart-idempotency.json), [default startup](../reports/v7-default-startup.json), integrity and live screenshots |
| README local links/images and shell examples | **43 README targets /6 shell examples;95 links across all current documents passed** | [Validation](../reports/v7-readme-validation.json) |

The final CI artifact ZIP SHA-256 was verified before copying its unedited screenshots and normalizing machine-specific path prefixes in JSON: `ff4f0fc54e8668cea82831b1fb5fbe65f91cd12bf7337f30bc76d0da8d2aaf8e`. Original ZIP and failures remain retained; test-result values were not edited.

The local standalone macOS attempt records **2 request tests passed /7 browser-launch failures**, all before UI assertions, with `bootstrap_check_in … MachPortRendezvousServer: Permission denied (1100)`. Managed browser installation succeeds. The same supported runner executes on Linux; the app is also exercised through real in-app browser automation locally. This environment restriction is not hidden by a green Linux run.

The first Linux run failed one backend test because the frontend had not yet been built; the order was corrected without weakening the security-header test. The next run passed7/9 browser tests and exposed mobile navigation/table-keyboard issues. A later stronger test walked the whole form after invalid-input recovery and caught the zero-value reset; final-step axe checks then caught unnamed completed mobile progress controls. Failed logs remain alongside successful evidence: [first](../reports/v7-ci-first-log.txt), [mobile/table failures](../reports/v7-ci-second-log.txt), [field-recovery failure](../reports/v7-ci-fourth-log.txt), [final-step naming failure](../reports/v7-ci-fifth-log.txt). No test was removed or conditionally skipped to get green.

## Recall investigation: original policy retained

The operating ceiling **70% extra-review routing** was declared before exploring the validation frontier. It is a provisional resource assumption, not a customer requirement or a universal fairness criterion.

- Validation contains300 records with98 positive labels. Original threshold≈0.50 / margin0.16 routes191/300 (63.67%) and catches83/98 positives (84.69%).
- The minimum-workload monotone score cutoff reaching90% is **0.2622583782022477** (equivalent margin0.23774162179775254 around the original threshold). It routes221/300 (**73.67%**) and catches89/98 (**90.82%**), leaving9 positives unflagged.
- This would add30 extra-review cases per300 validation cases to catch6 more positives. No eligible cutoff stays within the provisional70% ceiling.
- **No replacement was selected.** Original `models/config.json` remains byte-identical; the90% active target remains unmet. The candidate was not evaluated on final test or used to train a new model. No claim of impossibility beyond this monotone-score/capacity investigation is made.

`ml/validation_policy.py` loads validation only; an automated test rejects any other CSV read during that analysis. `scripts/audit_v7.py` writes that decision before running descriptive held-out investigations under the unchanged original policy.

## Fairness investigation: descriptive findings retained

| Group | Cases / positive / negative | Positive rate | Classifier FN / positives | FNR | Uncertain cases | Extra-review route | Missed positives after original uncertainty routing |
|---|---|---:|---:|---:|---:|---:|---:|
| Audit A |130 /41 /89|31.54%|14 /41|34.15%|35|66 /130 (50.77%)|9|
| Audit B |102 /32 /70|31.37%|3 /32|9.38%|34|65 /102 (63.73%)|1|
| Audit C |68 /23 /45|33.82%|9 /23|39.13%|28|41 /68 (60.29%)|2|

Label balance is similar but does not equalize case mix or error rates. B has more reported conflicts (16.7%) and specialist requests (20.6%) than A(13.1%,14.6%) or C(11.8%,10.3%). Mean missing categories are0.38/0.48/0.43; unclear-housing shares13.8%/13.7%/17.6%. Mean information completeness is83.4/82.3/83.6. These are observed associations, not a causal explanation for FNR differences.

The FNR gap remains **29.76 percentage points**, with original potential-concern flags for B/C. The flag uses absolute difference and is not a normative conclusion that every flagged group is disadvantaged in the same way. Numeric one-hot proxy correlations have maximum absolute value≈0.148; low pairwise correlation cannot rule out nonlinear or combined proxies.

There are97 uncertain cases; union with111 class-positive cases routes172 cases. These counts overlap and must not be added directly. Remaining-route errors are12/128 versus26/189 under class-only routing; populations differ, so this is not a causal improvement or observed service saving. These benchmark routing rates do not include the new live input-range safeguard.

All200 excluded-audit-label pairs have identical scores/classifications by construction. The interface now explicitly says: **“Identical paired predictions do not establish absence of proxy discrimination.”**

## Training/input consistency and preserved evaluation

The generator sets information completeness to `clip(100 -18×missing - Normal(8,12),5,100)`, rounded to one decimal. It is not the three-document percentage. Mapping to100/66.7/33.3/0 compressed a noisy training distribution into four values and introduced0 outside the observed training range **21.1–100**.

V7 keeps the same supported input field and separates it from calculated document completeness. The declared score is explicitly synthetic and requires a defensible caseworker measurement protocol before any real-world use. Training-only range/category checks flag absent categories, out-of-range values and values handled by the fitted imputer; flagged cases require human handling even when a genuine probability can be calculated. These checks cannot detect all semantic or distribution mismatch.

Fitted feature order matches the nine allowed features. Numeric imputer statistics match training medians; housing uses the training-fitted most-frequent imputer and one-hot encoder. Unknown housing is rejected by the submission schema; direct low-level inference flags unknown encodings for human review. Missing required submission fields return422 rather than silent defaults.

Original model SHA-256: `bd4add37db3308b56a51410d215b4012b37384b84a450f137ccfabb1e8174655`.

Original held-out results remain **accuracy77.6667%, precision63.0631%, recall72.9167%, F1 67.6329%, AUC0.81929126**, matrix `[[163,41],[26,70]]`. Checklist recall remains91.6667%. Source2,000 and split1,400/300/300, separate400-row/200-pair fixture, reproducible generation and zero scenario/application overlap all pass. All ten canonical inputs and every original source path remain intact. [Protected hashes](../reports/v7-protected-artifacts.json).

## Actual browser journey and failure demonstration

Local real-browser reference **DEMO-b38e22c9** used household4, income£1800, Stable housing, missing income evidence, independently declared information completeness80, no conflict/specialist request. Actual saved RF probability is **0.46126532203493115** (46.1%); documents are2/3=66.7%. Uncertainty requires human escalation despite the class-only routine prediction. Tree SHAP reconciles to the same score with additivity error **4.773959005888173e-15**.

The administrator found the same reference, ran inference/SHAP, requested information with a reason, then completed administrative review with another reason. The applicant saw both updates; reload and full backend stop/start retained all four events. A separate retry probe, **DEMO-e25bcedd**, returned the same reference with `Idempotency-Replayed:true` after a full backend process restart and retained only one submission event. Browser tests also simulate losing a success response after the server commits, reload and retry with the same key, and prove that the session has only one record.

A real stopped-backend check displayed Service unavailable and recovered on Retry. An **isolated port8002 fault-injection server** made only the in-memory artifact loader raise controlled `OSError`; no artifact file changed. The UI showed Model unavailable, no score and no fabricated SHAP; the caseworker recorded an actual escalation in that isolated DB. This found and fixed the misleading success toast: it now says **“Model inference unavailable. Human review fallback saved.”** Healthy inference still reports actual model use. The fault server was stopped after verification.

Genuine screenshots: [overview](screenshots/v7-live-overview.png), [assessment](screenshots/v7-live-assessment.png), [applicant completion](screenshots/v7-live-applicant.png), [fairness](screenshots/v7-live-fairness.png), [service outage](screenshots/v7-live-outage.png), [controlled model fallback](screenshots/v7-live-model-fallback.png), plus the versioned CI viewport screenshots and artifact provenance.

## Database, reset and local security boundary

Fresh default startup uses **`.test-runtime/sandbox.db`** with12 independent UI scenarios. The old **`habitat.db` remains13 applications /27 events**, row-for-row unchanged. Browser verification uses `.test-runtime/v7-browser.db`; original V6/private test DBs remain retained. No local database is committed or packaged.

The retry-key table stores a hash of the session/key namespace and a normalized payload hash with its application reference. SQLite `BEGIN IMMEDIATE` makes lookup+insert one transaction across connections. Duplicate/simultaneous retries return the saved reference; mismatched data under the same key returns409; invalid input returns422; failed storage rolls back without reserving a key. Application history remains append-only. UUID session IDs are grouping keys, not identities or access control.

Reset is deliberately limited to the named default sandbox file. With the backend stopped, it first makes a recoverable SQLite backup with a unique name, then recreates the independent scenarios. Two actual resets and backup contents were checked. Public datasets, splits, model, saved evaluation and historical evidence are untouched.

Active SQLite files are0600 on POSIX. Current frontend/backend listeners were verified at127.0.0.1 only. CORS permits localhost/127.0.0.1 port5173 and the required headers, not arbitrary public origins. TrustedHost rejects unrecognized public Host headers. API no-store, fixed-path downloads and entrypoint security headers remain tested.

These controls do **not** provide production security. Local clients can access applications by reference and call admin actions without credentials. Reviewer identity, authentication/RBAC, tenant isolation, encryption, privacy governance and adversarial security assurance remain absent. A synthetic declaration cannot detect all misuse, especially free-text notes. Do not enter real personal records or expose the service to the public internet.

## Startup, reset and verification commands

From the repository root after the pinned installation/build in README:

```bash
# Terminal 1: independent default sandbox, loopback only
MPLCONFIGDIR=/tmp/habitat-matplotlib bash scripts/start_backend.sh
# Terminal 2: both portals share this backend
bash scripts/start_frontend.sh
```

Open `http://127.0.0.1:5173`; API docs are `http://127.0.0.1:8000/docs`. `HABITAT_DATABASE_URL` overrides the default; `.env.example` is a reference, not automatically loaded.

```bash
# Backend stopped: backup and restore only the named default sandbox
MPLCONFIGDIR=/tmp/habitat-matplotlib .venv/bin/python -m scripts.reset_sandbox
# Build first: backend entrypoint/header tests require the production bundle
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run build
MPLCONFIGDIR=/tmp/habitat-matplotlib .venv/bin/python -m pytest -q
MPLCONFIGDIR=/tmp/habitat-matplotlib .venv/bin/python -m scripts.audit_v7
.venv/bin/python -m scripts.contrast_v7
.venv/bin/python -m scripts.validate_readme_v7
npm --prefix frontend run browser:install
npm --prefix frontend run test:e2e
```

On Linux CI use `npm --prefix frontend run browser:install -- --with-deps`. On this restricted macOS execution host, test launch remains denied; running the same command does not guarantee escaping an OS/process restriction. The supported Linux workflow records the complete suite without disabling tests.

## Remaining FAIL / NOT TESTED boundaries

- **FAIL:** active90% validation target, retained honestly at84.69%. No selected replacement or new test-based tuning.
- **FAIL on this macOS execution host:** standalone browser launch; Linux execution is separately reported.
- **NOT TESTED / not established:** real-world housing usefulness/fairness, calibrated approval/entitlement probabilities, causal fairness, production authentication/security/deployment, physical mobile touch and screen-reader/Safari/Firefox/full-WCAG review.
- Buyer capacity, prices, costs, pilot and second-customer plan remain hypotheses. Team names and a genuine video are still human-supplied items.
- Fifteen Python dependency deprecation warnings remain; CI action-runtime warnings are preserved in logs. No claim of a flawless product is made.

No critical core-workflow defect may be treated as ready while unresolved. Final readiness is limited to the specifically verified **local synthetic demonstration** and the final-source test evidence above.
