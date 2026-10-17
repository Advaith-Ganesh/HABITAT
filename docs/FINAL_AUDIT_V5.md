# Final audit V5 — 17 October 2026

**Ready for the tested local synthetic demonstration. Not a production housing service.** Work continued in the existing repository from checkpoint `ce008d6`, branch `habitat-v5-refinement`. No model retraining, source CSV replacement or original database writes were needed. Actual live986px and1280px layouts were inspected; the standalone exact-viewport/axe matrix remains unexecuted.

## Verification matrix

| Feature | Test performed | Status | Evidence | Fix performed | Remaining issue |
|---|---|---|---|---|---|
| Warm/petrol/sage UI, branding | Real browser and token contrast | PASS | Genuine v5 screenshots at986/1280px without observed page overflow;22 sampled contrast pairs | Updated SVG/favicon, palette, compact cards and form hierarchy | Full WCAG/assistive-technology review not executed |
| Portal navigation | Real browser3/5 labels, routes, role switch | PASS | v5-live-browser.json | Full icon+text labels and exact requested tabs retained | Demo switch is not authentication |
| Applicant submission and validation | Native invalid household blocked, then real POST | PASS | DEMO-849ed9ee, unassessed,66.7% docs | Preserved validated form and reference storage | No personal document upload/response feature |
| Live dashboard values | Cross-tab UI+API+SQLite stage comparison | PASS | Total13→14; unassessed0→1→0; pending5→6→5; requests0→1→0; completed1→2 | Added completed count and event-driven cross-tab invalidation | Other browser sessions need Refresh; no push service |
| Application list/status | Search and saved latest-event comparison | PASS | Information request appears in list and tracking | Added batched latest-review enrichment | Original historical statuses intentionally unchanged |
| Real model and feature mapping | Direct loaded Pipeline vs API; relevant and excluded-input cases | PASS | v5-ml-audit.json; pytest | Preserved one model; equal outputs not artificially changed | Synthetic labels do not establish external validity |
| SHAP | Actual score/additivity/sign/feature tests and browser chart | PASS | New case53.1%, Tree SHAP; numerical additivity receipt | Plain signed summaries and explicit loading/unavailable states | Associations only; correlated inputs limit attribution |
| Human follow-up/reassessment | Request → reassess → queue remains pending | PASS | Browser case history and new routine-score regression | Inference can no longer clear an open caseworker request | Administrator identity not authenticated |
| Human completion/applicant tracking | Saved reason; cross-tab update; reload | PASS | Applicant sees resolved administrative review | Refetch and storage-event updates | Completion never means allocation |
| Held-out report metadata | Recompute and bind date to10 artifact hashes | PASS | evaluation_verification.json, model metadata endpoint | Removed repeated sample literals; added honest verification date | Historical creation timestamp was not recorded |
| Fairlearn and paired suite | Actual recomputation, group filter and pair view | PASS | n130/102/68;200 pairs/400rows; saved JSON unchanged | Backend-derived row/pair/example counts | Invariance expected from excluded attribute |
| Fairness equality | Compare group FNRs | FAIL | Max–min29.76pp, two concern flags | Kept visible; no invented mitigation | Small synthetic groups; no causal conclusion |
| Validation recall target | Compare84.69% to90% target | FAIL | Original model config/evaluation | No test tuning or retraining to conceal failure | Target remains unmet |
| Uncertainty safeguard | Recompute errors before/after existing routing | PASS |67/300 baseline;26/189 then12/128 remaining-route errors;37%→57.33% workload | Added before-any-escalation baseline | Remaining populations differ; no real outcomes or savings measured |
| Dataset/provenance/download |2000 rows, byte regeneration, schema, split isolation, actual endpoint bytes | PASS | v5-integrity.json; v5-ml-audit.json | Documented project generation and separate fairness suite | Not observed government records |
| Full backend/API suite | pytest after repairs | PASS |78 passed;15 dependency warnings | Added6 meaningful V5 regressions | Dependency deprecations remain |
| Frontend checks | ESLint/TypeScript/Vite | PASS | Versioned execution logs | Repaired discovered label/typing issues; restored unchanged dependency entries after version-metadata review | No browser-based load/performance benchmark |
| Standalone request-only test | Playwright API fixture | PASS | CSV2000rows and original matrix | Existing test retained | Not a browser assertion |
| Standalone browser runner |5 attempted cases | FAIL | Chromium launch aborted before assertions | Used working in-app browser for full journey | No runner/browser assertions counted as passed |
| Exact375/768/1280 and axe | Runner launch attempt | NOT TESTED | v5-e2e-output.txt | Responsive CSS and keyboard behavior retained | Requires a host where Chromium launches |
| README links/assets/commands | Local targets, shell syntax, actual startup/test execution | PASS | v5-readme-validation.json | Premium showcase with real screenshots and grounded evidence | npm-ci dry-run passed; fresh clean installation/retraining not rerun in V5 |
| Full retraining command | Reviewed stage order and shell syntax | NOT TESTED | reproduce.sh; no fitting executed | Refresh verification after intentional evaluation | Preserve current model; run only when explicitly needed |
| Production security/legal validity | Scope review | NOT TESTED | Sandbox disclosures, SECURITY.md | Explicit RBAC/privacy limitations | Authentication, tenant isolation, expert labels and legal validation required |

## 1. UI refinement

Warm off-white#F7F6F2, ink#1A2736, petrol#285568, sage#4B837A and stone#E7E5DF. Dark mode retained. Original home/H SVG is reusable at favicon size. Full form appears on applicant landing, transparency, README and demo docs. Main comparison sections are Model Performance, Fairness Across Groups and Compare Two Applications, with concise expandable help. Probability wording is explicitly model-estimated additional review.

## 2–3. Dynamic and static values

[DATA_VALUE_AUDIT_V5.md](DATA_VALUE_AUDIT_V5.md) maps all active displayed-number families to live DB(A), calculated application(B), fixed model/dataset evidence(C), explicit business assumptions(D), or repaired issues(E). Stable evaluation figures are legitimate and labelled; live totals are not hard-coded. Mutation-driven refresh works within and across same-origin demo tabs without interval polling. Reassessment preserves human follow-up, including when the new model route is routine.

## 4–6. Actual model, explanation and fairness findings

One fitted180-tree Random Forest, train-only preprocessing,1,400/300/300 group-isolated splits. Test accuracy77.67%, precision63.06%, recall72.92%, F1 67.63%, ROC-AUC0.8193; matrix[[163,41],[26,70]], n300. Checklist recall91.67% is higher than model recall. Threshold≈0.50/margin0.16 come from validation; desired validation routing recall90% remains missed at84.69%.

The live case scored0.5305952150 with real SHAP and uncertainty escalation. Documentation remained a separate66.7% ratio from two declared categories. Audit A/B/C FNR34.15/9.38/39.13%, FPR17.98/22.86/20.00%, counts130/102/68. Paired attribute changes yieldzero score/class differences as expected; no absence-of-proxy-bias claim. Changing a genuine conflict input in the interactive comparison produced14.9%→65.1%, actual changed SHAP and no saved writes. Income changes legitimately give equal scores because it is excluded; tests ensure differences are not forced.

## 7–9. Provenance, sandbox and complete journey

The source2,000 records and independent400-row paired fixture are project-generated, public and reproducible. No observed government cases or real personal documents were introduced. All protected model/data/evaluation/fairness hashes match the safety baseline; original database rows remain intact. Browser writes used a clone. The full applicant→admin→inference/SHAP→request→reassessment→human completion→applicant reload journey passed. Machine-readable browser, endpoint and integrity evidence lives in reports/v5-*.

## 10–12. Documentation, files and launch

README now includes actual logo/screenshots, source-backed metrics and method tables, Mermaid architecture, stack, public download,70/15/15 splits, separate paired suite, setup/testing/retraining, API routes, business assumptions, international policy interface, limitations, AI disclosure, team/video placeholders and licences. No fabricated badges, testimonials or sponsors. Fixed the case-sensitive judge-Q&A filename so its GitHub link resolves. [Changed files](../reports/v5-changed-files.txt).

From the project root in separate terminals:

```bash
bash scripts/start_backend.sh
```

```bash
bash scripts/start_frontend.sh
```

Open http://127.0.0.1:5173. The final servers use an isolated V5 demo DB; canonical scripts use the original local database. Included trained artifacts work without fitting or API keys.

## 13–14. Remaining limitations and readiness checklist

- [x] Real synthetic applicant/admin round trip; actual model and SHAP.
- [x] Live counters update after persisted mutations; latest human status is consistent.
- [x] Dataset/model/report bytes and original DB preserved.
- [x] Model, baseline, Fairlearn, paired and safeguard results independently recomputed.
- [x] Backend suite and frontend lint/types/build executed; genuine screenshots and README links checked.
- [ ] Standalone browser assertions, exact viewport matrix and axe executed successfully.
- [ ] Validation recall target met; group disparities resolved with independent evidence.
- [ ] Production authentication/RBAC, tenant privacy, reviewer identity, expert outcomes and legal validation.
- [ ] Human team details and a real demo video supplied.

No critical core failure remains in the tested synthetic journey. Do not present this as production-ready or externally validated housing decision software. Submission readiness is limited to that tested demonstration.
