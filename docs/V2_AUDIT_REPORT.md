# HABITAT AI V2 audit

Date: 17 October 2026. Scope: local fictional intake-review sandbox. Existing React/Vite, FastAPI, SQLite, sklearn Pipeline, Tree SHAP and Fairlearn architecture retained. Safety checkpoint `b51b555` on branch `habitat-v2-audit`; original database backed up before edits. No model retraining or saved evaluation replacement.

## Product changes

Light and dark themes, self-hosted Inter, navy collapsible navigation, persistent theme/sidebar preferences, breadcrumbs, health indicator, consistent indigo/teal cards, focus styles and reduced-motion CSS. Reusable AppShell, MetricCard, DataTable, SearchInput, FilterBar, StatusBadge, ProgressIndicator, AuditFinding, ExplanationChart, EmptyState, ErrorState, SkeletonLoader, ConfirmationDialog, ToastNotification, HumanReviewPanel and PolicyReferenceCard. Navigation/header concerns remain grouped in AppShell rather than needless wrapper files.

All existing pages retained. Five-step validated fictional form with draft save/restore and reset confirmation; sortable/searchable/paginated case register and detail dialog; genuine SHAP plus input values; actual event activity; fairness rerun/filter/pair selection; versioned policy references; dataset dictionary/download; held-out comparison and transparent hypothetical economics.

## Executed audit matrix

| Feature | Method | Result | Evidence / practical limit |
|---|---|---|---|
| Overview | Browser plus HTTP counts vs SQLite | PASS | Real 14 test-clone applications, five pending, two resolved after smoke; no invented growth chart |
| Register | Browser search, pending filter, sorting, pagination, case drawer/Escape | PASS | Distinct five-row pages, descending sort, single HAB-0072 search result, dialog closes |
| Submission | Real browser, five sections, draft restore/reset, schema tests | PASS | DEMO-ad65338b persisted and assessed; explicit synthetic consent |
| Saved-model inference | Browser response vs direct loaded Pipeline | PASS | Exact score 0.7889516465798122; unchanged model SHA |
| Explainability | Real SHAP, feature alignment and additivity tests | PASS | Nine grouped inputs, base 0.5003233, additivity error 4.996e-15 for smoke case |
| Group fairness | Browser Run group analysis + API recomputation | PASS | Actual Fairlearn report equals stored fairness.json |
| Paired audit | Browser rerun + API recomputation | PASS | 200 pairs / 400 distinct paired rows, zero score/class differences; excluded attribute makes equality expected |
| Human review | Evidence request → reload pending → routine completion → reload resolved | PASS | Four persisted events; reasons survive backend process restart |
| Dataset | UI download bytes plus HTTP SHA and regeneration | PASS | Exactly 2,000 rows; public CSV SHA 196d2f715cbc959dac5c27e77d3db2edd31b6cafab1a0a296a9f445a8444f255 |
| Policy | Browser metadata/source and API/schema tests | PASS | England fictional prompts, source link; US/India/Singapore explicitly future integrations; legal adequacy not certified |
| Model Performance | Browser matrix, API equality, recomputed metrics | PASS | Matrix [[163,41],[26,70]], held-out n=300; validation clearly separate |
| Economics | Browser assumptions changed to volume 2000 and zero | PASS | Hypothetical arithmetic responds; zero per-case value explicitly undefined |
| Theme/sidebar/keyboard | Browser Enter switch, reload, collapse/expand, Escape | PASS | Dark persisted, sidebar 248→80px; visible focus styles |
| Desktop/tablet rendering | Genuine browser 1280 and 986px, overflow inspection | PASS | No page horizontal overflow in observed layouts; genuine screenshots |
| Exact mobile/tablet matrix | Standalone browser launch | NOT TESTED | 375/768 planned; Chromium aborted before assertions |
| Automated accessibility | axe within standalone runner | NOT TESTED | Browser launch blocked; no WCAG conformance claim |
| Sampled contrast | Source-token calculation, 17 pairs | PASS | All sampled normal-text pairs ≥4.5; not every rendered combination |
| Backend unit/API integration suite | pytest after repairs | PASS | 57 passed, 15 dependency deprecation warnings |
| Frontend lint/types/build | npm scripts after final source change | PASS | Zero lint warnings; tsc and Vite production bundle succeed |
| Standalone Playwright suite | Seven attempted cases | FAIL | Runner infrastructure: browser SIGABRT before test assertions; seven launch failures, zero test assertions counted as passed |
| ML/data preservation | Read-only audit + checkpoint hashes | PASS | All nine protected artifacts byte-identical; split scenario isolation; 180 fitted trees; no retraining |
| Original DB/source preservation | Compare all original rows to backup, checkpoint paths | PASS | 13 original apps, 27 original events unchanged; all 69 checkpoint files still present |
| Security basics | Source review, schema/API tests, header check, npm audit, key-pattern scan | PARTIAL | Fixed-path downloads, ORM queries, extra-field rejection, safe errors, security headers; zero npm advisories; no penetration test/authentication |
| Required validation recall | Compare saved metric with ≥90% target | FAIL | Actual 84.69%, disclosed in product |
| Group error equality | Compare held-out FNRs | FAIL | Max–min 29.76pp; small descriptive synthetic groups, no causal conclusion |

Detailed execution outputs: `reports/v2-pytest.txt`, `v2-lint.txt`, `v2-typecheck.txt`, `v2-frontend-build.txt`, `v2-e2e.json`, `v2-e2e-output.txt`, `v2-contrast.json`, `v2-ml-audit.json`, `v2-npm-audit.json`, `v2-live-browser.json`, `submission-smoke.json`. Earlier `*-first` logs retain discovered failures; final logs supersede them.

## Bugs and repairs

- Evidence requests, escalation and continued review now stay pending; routine completion resolves. Existing V1 historical rows preserved. Completed review reassessment/re-resolution returns 409.
- Explanation failure no longer removes human controls. Missing, failed or incompatible stored assessments give safe 409/503 rather than invented attribution; current/legacy SHAP array representations handled and dimensional alignment checked.
- Health checks fitted trees and DB. SQLAlchemy exceptions return a safe 503 without internal messages. Strict typed case/event outputs and extra-field rejection improve API consistency.
- Paired audit reruns are read-only; they no longer rewrite the public counterfactual CSV. Group audit exposes a real recomputation endpoint.
- Dashboard values derive from actual cases/events; recent rows retain backend timestamp order. The table previously overwrote this with alphabetical reference ordering; final browser check confirmed the new case appears first.
- Removed a decorative workspace dropdown. Reset confirmation now names its action. Dialog cancellation keeps React/native state synchronized. Retry after successful creation reuses the saved case ID if assessment subsequently fails.
- Light-theme muted/teal tokens adjusted after measured contrast failures. Percentage-chart axes now show unclipped 0/25/50/75/100% ticks after the final screenshot inspection found clipped labels. Chart tooltip/legend use neutral theme text. Zero-volume economics displays an undefined per-case cost instead of fabricated division.
- Route restoration and per-route fetches prevent empty case state after reload. In-flight GET deduplication reduces duplicate requests without caching stale writes. Lazy page/chart chunks reduce initial JS from about 589kB to 217kB (uncompressed); charts about 411kB load separately. This is bundle analysis, not a measured user-speed claim.

## Actual ML findings

One 180-tree RandomForestClassifier, depth 8, leaf minimum 8, balanced weights, seed 42; training-only preprocessing. Group-isolated 1400/300/300 partitions from 2000 synthetic records. Nine permitted model inputs; identity, audit group, income and accessibility request excluded. Threshold ~0.50 selected on validation only; margin 0.16. Test accuracy 77.67%, precision 63.06%, recall 72.92%, F1 67.63%, ROC-AUC 0.8193. With uncertainty escalation, test routing recall 87.5% and review rate 57.33%. Checklist recall 91.67% exceeds model recall: no universal superiority claim.

Audit A n130 FPR17.98% FNR34.15%; B n102 FPR22.86% FNR9.38%; C n68 FPR20.00% FNR39.13%. Two potential-concern groups by the documented heuristic. Counterfactual invariance does not test all proxies; max observed numeric-input/group correlation about 0.148. No calibrated certainty, real-world fairness or legal compliance is established.

## Security and limits

No external housing actions, council integrations or runtime LLM calls. Inputs allow fictional structured fields only; frontend uses React text rendering; fixed download paths; ORM queries; no destructive API routes. API no-store, nosniff, frame denial, referrer restriction and same-origin HTML CSP are applied. Self-hosted Inter avoids a font-service request; SIL licence copied into docs/third_party.

This remains an unauthenticated loopback sandbox. No verified reviewer identity, tenant isolation, formal adversarial test, rate limiting, production encryption or administrator-proof logging. Append-only SQLite triggers cannot constrain an administrator. Synthetic declarations cannot detect all real data. Source key-signature scan and npm audit are bounded checks, not proof of security.

Mobile focus trapping and responsive CSS are implemented but the exact mobile execution is NOT TESTED. Manual follow-up: on a separate test DB run `npm run test:e2e` on a machine where Playwright can launch Chrome; inspect 375/768 widths, keyboard modal navigation and axe results. Do not reinterpret launch failures as application assertions passing.

## Handoff

Use README startup commands and DEMO_CHECKLIST.md. Demonstrate genuine inference, an honest fairness warning, and a persisted human action. Do not call this housing approval software. The scoped synthetic desktop demonstration is submission-ready; real-world deployment is not. All original source paths, data/model/report bytes and original database rows were preserved.
