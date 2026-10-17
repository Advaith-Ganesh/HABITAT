# Judge questions and grounded answers

## 1. What does HABITAT predict?

Additional human intake-review need under a fictional protocol. It never determines housing eligibility or allocation.

## 2. Who uses it and who might pay?

Caseworkers are the users; housing authorities, programme operators, NGOs and housing associations are proposed buyers, not signed customers.

## 3. Is the dataset real?

No. Exactly 2,000 generated fictional rows from 1,000 related scenario families; generator seed 42 is reproducible.

## 4. How are related rows separated?

Scenario-family group splits are 1,400 training, 300 validation, 300 test. Application and scenario intersections are checked to be empty.

## 5. What are the labels?

A documented synthetic additional-review label generated from fictional intake conditions and noise. Agreement with it is not external housing validity.

## 6. Which model runs?

The saved sklearn Pipeline contains one RandomForestClassifier with 180 trees, depth 8, minimum leaf 8, balanced weights and seed 42.

## 7. Did the redesign retrain it?

No. All nine protected dataset, split, model/config and evaluation/fairness report hashes match the checkpoint.

## 8. What preprocessing is fitted?

Numeric imputation and categorical imputation/one-hot encoding inside the Pipeline, fitted on training data only.

## 9. What are the actual test metrics?

Accuracy 77.67%, precision 63.06%, recall 72.92%, F1 67.63%, ROC-AUC 0.8193 on 300 held-out rows.

## 10. What does the confusion matrix contain?

163 true negatives, 41 false positives, 26 false negatives and 70 true positives. Positive support 96; negative support 204.

## 11. Is it better than the checklist?

Not on every metric. The deterministic checklist recall is 91.67%, above model recall 72.92%; model accuracy and precision are higher.

## 12. How is the threshold chosen?

By validation-only F1 over fixed candidates; selected threshold approximately 0.50. The final test set was not used for selection.

## 13. What happens near the threshold?

A 0.16 uncertainty margin routes ambiguous scores to human review; test routing recall 87.5%, routing review rate 57.33%.

## 14. Was the target met?

No. Desired validation routing recall 90%, observed 84.69%. The UI exposes that failure.

## 15. Are probabilities calibrated?

No calibration study was completed. The UI calls them estimated scores and explicitly disclaims guaranteed certainty.

## 16. Are explanations real?

Yes. Tree SHAP is computed on the saved model; transformed contributions aggregate to original feature groups. Additivity is tested.

## 17. Does SHAP establish causation?

No. It describes model associations relative to a base value; correlated inputs and group aggregation limit interpretation.

## 18. Which attributes are excluded?

Audit group, identifiers, income, household/bedroom/cost details and accessibility-request fields are outside the nine-feature inference allowlist. Specialist-support request is included and needs expert governance.

## 19. Does exclusion ensure fairness?

No. Other inputs may encode proxies. Synthetic error rates and correlations cannot establish universal or legal fairness.

## 20. What did Fairlearn find?

Audit A n130 FNR34.15%, B n102 FNR9.38%, C n68 FNR39.13%; max–min FNR gap29.76pp. B and C trigger the documented potential-concern heuristic.

## 21. What do paired tests prove?

200 separate pairs change only the audit group; scores/classifications are identical because that field is excluded. This limited invariance does not rule out proxies.

## 22. Can a human override the model?

Yes, with a mandatory meaningful reason. Evidence request, escalation and continued review stay queued; routine completion resolves the intake workflow.

## 23. Does a completed review allocate housing?

No. It only completes this fictional intake review. Every real housing decision remains outside the app.

## 24. How is review history stored?

SQLite events have timestamps and reasons, with triggers blocking UPDATE/DELETE. Administrators can still modify the database; this is not tamper-proof identity assurance.

## 25. What if the model or explanation fails?

Inference errors return a human fallback with no fabricated score. Explanation errors preserve human-review controls and return safe errors; failed health checks show degraded service.

## 26. Which policies are implemented?

England metadata links general statutory guidance, but functional intake prompts are explicitly fictional. US, India and Singapore are future integrations.

## 27. Is there a production integration?

No council API or live allocation endpoint exists. It is a local synthetic sandbox with no authentication or tenant isolation.

## 28. What is the proposed pricing?

Starter £299/month and Institutional £999/month are unvalidated hypotheses. The calculator exposes human-time, wage, volume and infrastructure assumptions.

## 29. Are savings demonstrated?

No. Calculator outputs are hypothetical arithmetic, not observed customer savings. Zero-volume per-case costs are undefined.

## 30. What would a first pilot require?

Expert-labelled and lawfully governed data, subgroup outcomes, caseworker usability, identity/security controls, local policy verification and measured costs before operational use.

## 31. What testing really ran?

V7 has111 passing backend/API tests plus lint, TypeScript, production build and real in-app browser checks. The complete Linux Playwright suite covers9 tests and375/768/1280 viewport/axe checks; see V7_FINAL_REMEDIATION_REPORT.md for the exact final source run. Restricted local macOS still has2 request passes and7 browser-launch failures before assertions. These environments are reported separately.

## 32. What would you show judges?

One new fictional case, genuine score/SHAP, the visible fairness concern, an evidence request with persisted history and real dataset/evaluation artifacts.

## 33. Where is AI used in development/runtime?

Codex assisted implementation, tests, synthetic generation and documentation. Runtime inference uses local sklearn; no paid LLM service is required.

## 34. Can this be submitted as production-ready?

No. Only the verified local synthetic demonstration is in scope. The active validation target is missed and subgroup disparities remain. Linux browser viewport/axe checks do not establish production security, physical-device/screen-reader accessibility or real-world housing fairness.


## 35. What changed in V4?

Three applicant links and exactly five administrator tabs. Submission saves before inference; administrators assess, inspect SHAP and record actions that update applicant status. The original model, dataset and evaluation remain unchanged.

## 36. How is document completeness calculated?

Three declared demo categories: income, identity and current-housing evidence. Present/3×100, so two present is66.7%. It is separate from model probability and not a statutory requirement. V7 also separately declares the broader intake-information completeness input; its real-world measurement remains unvalidated. All eight document-flag combinations are tested.

## 37. What measurable safeguard did you evaluate?

Existing validation-selected uncertainty escalation increases human routing37%→57.33%, leaving12/128 errors(9.375%) versus26/189(13.76%) without added uncertainty. Remaining populations differ. No real-world benefit or observed savings is established.

## 38. Is the portal switch secure authentication?

No. It is a demo-only role switch with openly loadable synthetic references. Production requires authentication, RBAC and tenant isolation. No real personal documents should be entered.


## 39. Why do some dashboard values stay constant?

Held-out evaluation values intentionally stay constant for fixed model/data artifacts and are labelled accordingly. Live application/status counters query SQLite and refetch after mutation events. V7_FINAL_REMEDIATION_REPORT.md documents current sources, changed input mapping and preserved historical evidence.

## 40. What does the evaluation date mean?

The hash-bound sidecar records the actual read-only recomputation time. It does not invent an original training/evaluation timestamp. If bound artifacts change, the API marks that verification as stale rather than showing its date as current.
