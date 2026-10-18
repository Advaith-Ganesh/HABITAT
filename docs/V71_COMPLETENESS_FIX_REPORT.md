# V7.1 applicant completeness fix

18 October 2026 · dedicated branch `fix/v7-1-applicant-completeness`.

## Root cause and training definition

The applicant form exposed an internal Random Forest feature and initialized it to95. Backend `Case` also defaulted it to95. Neither value measured the applicant's information quality. V7 separated this field from document completeness but still relied on an applicant guess.

The [unchanged generator](../data/generate_dataset.py) creates the feature as `round(clip(100 - 18 × missing_document_count - Normal(8,12),5,100),1)`. The random term is not an observable applicant declaration. Training contains1,400 values: min21.1, Q1 72.275, median84.2, Q3 96.1, max100, mean82.2553 and standard deviation15.2923. The pipeline's fitted median imputer is84.2; that is **not** a defensible replacement measurement. Nine features, their order, classifier/configuration and original evaluation remain unchanged. [Training source](../ml/train.py), [input-range checks](../ml/input_audit.py), [prediction source](../ml/predict.py), [saved configuration](../models/config.json).

**Compatibility from visible applicant fields is not established.** Document completeness is a separate three-category declaration ratio. A deterministic document percentage, filled-field ratio, conditional mean or hidden constant would not recover the generated latent value. No new intake percentage is invented. Real-world completeness measurement remains unvalidated.

## Targeted handling

- The editable percentage, frontend95 and backend95 defaults are removed. All factual questions, five form steps and existing CSS/design remain.
- The server stores the authoritative feature as `null` for **every new submission**. A legacy client may include a bounded numeric value, but it is ignored. Invalid types/ranges still fail schema validation. Internal completeness is no longer a required submitted field; all14 factual/consent fields remain required.
- Before model execution, new records take the existing human-review fallback: `score=null`, `classification=null`, `requires_review=true`, failure `InputCompatibilityUnavailable`. No classifier, median imputation or SHAP runs for these cases. Read-only sensitivity uses the same gate; the explanation endpoint returns409. The interface explicitly explains why and displays no score or SHAP chart.
- “Calculated intake completeness” is shown as **unavailable**, not as a substituted percentage. Historical values are labelled historical recorded inputs, not newly calculated or validated. Existing numeric-input records and benchmark RF/SHAP remain available; their stored assessments are not rewritten.
- Canonical retry hashes ignore the untrusted score. Exact pre-upgrade request hashes also replay their original historical records. Browser draft restoration strips the obsolete control; an unconfirmed historical request retains its original payload/key across retries until acknowledged.

**New applications do not receive model predictions in V7.1.** This is the required safe outcome until a compatible measurement protocol or separately validated model design exists. Human review and applicant tracking remain functional. No retraining, benchmark tuning or paid API was introduced.

## Actual workflow — PASS

Real-browser submission **`HAB-F006510E`** used household5, income£1,950, stable housing and missing housing evidence, with no applicant completeness value. SQLite saved `null`. The administrator searched the same reference and assessed it: no model probability or SHAP; document completeness66.7%; explicit input-integrity human fallback. A caseworker saved:

> Please clarify the missing housing evidence. This application requires human review without a model score.

The applicant saw the updated request after reload. A full backend process stop/start preserved the case, assessment and three history events; both portals were refreshed. Separate real retry probe **`HAB-1D468C96`** ignored injected scores95/0/100/null and replayed one reference before and after restart, retaining one submitted event. The original historical `HAB-17F6A5CE` still returned score0.4158352705939491 and genuine SHAP with additivity error5.384581669432009e-15. No success response was simulated for this live journey.

[Form without percentage](screenshots/v71-factual-form.png) · [Honest assessment fallback](screenshots/v71-input-fallback.png) · [Applicant after restart](screenshots/v71-applicant-after-restart.png) · [Integrity and workflow evidence](../reports/v71-integrity-workflow.json).

## Files modified

Production: `backend/main.py` (schema, authoritative payload, compatibility gate and legacy retry); `frontend/src/main.tsx` (factual form/draft/retry handling and help); `frontend/src/components/NewCaseForm.tsx` (remove one field); `frontend/src/components/ReviewWorkspace.tsx` (honest historical/unavailable labels and SHAP gate). No styles, model or dataset files changed.

Tests: `tests/conftest.py` supplies isolated historical numeric-input records for legacy regression tests; API/V2/V4/V5/V6/V7 tests distinguish new fallback from legacy genuine inference; `tests/test_v71_completeness.py` adds injection, no-model-call, retry and historical compatibility proofs; `frontend/e2e/habitat.spec.ts` exercises the factual-only fallback journey, retains legacy SHAP/error tests and adds score-injection protection. No tests are skipped.

Documentation/evidence: this report, a brief README safety notice, updated product walkthrough, three actual screenshots and versioned V7.1 verification records. Original model/data/evaluation reports, charts and database rows remain intact.

## Verification

| Check | Result |
|---|---|
| Python suite | **PASS:119 tests**,15 dependency deprecation warnings; the old “score is required” parametrization is replaced by explicit optional/untrusted-score cases |
| ESLint / TypeScript / production build | **PASS** |
| Live factual submission, fallback, human action, applicant status, restart and retries | **PASS** |
| Client score injection and historical replay | **PASS**: bounded client values cannot change the saved feature; pre-upgrade exact retries remain compatible |
| Original model/data/evaluation hashes and original DB rows | **PASS**, see integrity evidence |
| README exact-case links and shell syntax | **PASS:59 exact-case targets and5 shell examples parsed**; historical validator evidence preserved |
| Supported Linux Playwright / GitHub Actions | Pending PR verification; merge is conditional on success |

## Limits retained

The original84.69% validation routing recall still misses90%; subgroup disparities remain. Benchmark evidence does not validate real housing use. New applications deliberately have no model score or SHAP because compatibility is unestablished. Production authentication/RBAC and real-world validation remain unimplemented. Prior restricted-macOS standalone Chromium launch limitations remain documented; this change uses real in-app browser verification and supported Linux CI. Historical numeric inputs remain historical, not retrospectively validated.
