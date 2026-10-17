# Model card · HABITAT intake-review model v1.0

Intended users: caseworkers demonstrating fictional intake workflows. Not intended for real applicant decisions. One RandomForestClassifier (180 trees, max_depth 8, min_samples_leaf 8, balanced class weights, random_state 42, n_jobs 1) was fitted on 1,400 synthetic records. No other production classifier was trained. A deterministic checklist is the comparison, not a second trained model.

## Training and selection
Numeric SimpleImputer(median), categorical SimpleImputer(most_frequent) and dense OneHotEncoder(handle_unknown=ignore) are fitted on training data only inside ColumnTransformer and Pipeline. No feature scaling. See models/config.json for the exact nine-feature allowlist. The fixed forest configuration was selected as a hackathon design choice, not searched on test data. Thresholds .3 to .7 in .025 steps maximise validation F1. Selected threshold: approximately .50. Uncertainty candidate margins: .04/.08/.12/.16. Pick the smallest achieving at least 90% validation routing recall, otherwise .16. No candidate met target: selected .16 gives validation routing recall 84.7%. This is an unmet safeguard target, not successful calibration. Scores are uncalibrated model estimates, not real-world correctness probabilities.

## Test evidence
300 held-out rows / 150 scenario families; 96 positive, 204 negative labels. Accuracy 77.67%, precision 63.06%, recall 72.92%, F1 67.63%, ROC-AUC 0.8193. Confusion matrix [[163,41],[26,70]]. FPR 20.10%; FNR 27.08%. Classification review rate 37%; uncertainty routing review rate 57.33%, with routing recall 87.5% (12 positive labels not escalated). Routine handling always remains human.

The checklist achieves accuracy 64.00%, recall 91.67%, F1 61.97%, review rate 62.67%. The forest has better accuracy and F1 here, but materially worse recall; it does not dominate the checklist. No statistical significance or external utility is asserted.

## Fairlearn descriptive audit
Selection means additional intake review, never housing allocation. Rates below use thresholded model classification, without the uncertainty routing band.

| Group | n | Selection | Accuracy | FPR | FNR | Finding |
|---|---|---|---|---|---|---|
| Audit A | 130 | 33.1% | 76.9% | 18.0% | 34.1% | No concern detected in this test |
| Audit B | 102 | 44.1% | 81.4% | 22.9% | 9.4% | Potential concern |
| Audit C | 68 | 33.8% | 73.5% | 20.0% | 39.1% | Potential concern |

FNR max–min gap 29.76% (percentage-point interpretation). A status requires at least 20 positive and 20 negative labels; concern means absolute FNR difference from the overall rate above .10. This heuristic is prewritten and descriptive. Confidence intervals and multiple-testing adjustment are not implemented. Observed differences may reflect sampling variation and generator associations; investigate before any pilot. No universal fairness interpretation is justified.

200 separate paired comparisons vary only synthetic audit group: zero classification differences; mean and maximum score difference zero. Attribute excluded, hence equality is expected. Largest absolute numeric-input/audit-membership Pearson correlation 0.1478. Low pairwise correlation does not exclude combined/nonlinear proxy behaviour. Audit groups are fictional, not protected classes; real protected-group validation remains outstanding.

## Explanation
Actual shap.TreeExplainer on the fitted forest, applied to transformed inputs. Positive-class encoded category values are summed back into original feature groups; numeric contributions remain original groups. Additivity is checked against predict_proba. Tree SHAP uses the tree-path-dependent default, not an interventional causal model. Correlated evidence fields can divide attribution in unstable ways. Deterministic prose reports actual attribution signs, never policy reasoning. Missing artifacts/features trigger human-review fallback with no invented score.

## Limitations, governance and security
Synthetic-label agreement is circular and not external validation. No confidence intervals, calibration validation, longitudinal drift evaluation or independent housing-expert labels. Wider API ranges can be out of distribution. Classifier and uncertainty band can miss review needs. Support flags require expert governance in real use. No real housing decision, eligibility calculation, allocation or rejection is supported. Local loopback sandbox; no authentication, tenant isolation, encryption-at-rest, trusted identity on overrides or production rate limiting. SQLite append-only triggers deter normal API/SQL mutation, but a database administrator can alter triggers/files. No tamper-proof cryptographic audit claim is made. Sandbox checkbox cannot detect a user who enters real data. Human review is required for all workflows.

Maintainer: hackathon team (names to be supplied). Documented benchmark/reference date: 2026-10-17; the original creation timestamp is not embedded in the old evaluation JSON. Python 3.12.14; direct dependencies pinned; full installed versions in requirements-lock.txt. Licence: MIT code/model, CC0 original generated records.

## V4 workflow and measured safeguard

One saved model is retained without retraining. Applicant submission now saves an unassessed case; an administrator explicitly runs inference. The three declaration flags determine a separate document percentage; new form submissions also use this percentage as the existing intake-completeness input. Historical benchmark inputs remain unchanged. This input-mapping choice does not establish external validity.

At existing validation-selected threshold≈0.50/margin0.16, additional-class-only escalation is111/300(37%) with26/189 remaining-route errors(13.76%). Adding uncertainty escalation is172/300(57.33%) with12/128 remaining-route errors(9.375%). Extra human workload20.33pp; remaining-route error difference−4.38pp, among different remaining populations. These are synthetic routing measurements, not observed housing outcomes. See reports/v4-safeguard.json.

## V5 verification provenance

No retraining occurred. Read-only verification binds the current model/config, public data, splits and evaluation/baseline/fairness reports to a recorded recomputation timestamp. The original evaluation creation timestamp is not embedded in the old JSON. See reports/evaluation_verification.json and reports/v5-ml-audit.json. Model metrics stay fixed until artifacts change. Before any human escalation the test classifier has67/300 routing errors(22.33%); remaining-route errors are26/189 without extra uncertainty and12/128 with it. Reassessment cannot clear an open human follow-up.
