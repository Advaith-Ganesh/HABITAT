# HABITAT AI — judging evidence and two-minute pitch

The weights below are the user-supplied SotonShip Responsible AI rubric, not a claimed judge score.

| Criterion | Weight | Concrete evidence and honest limit |
|---|---:|---|
| Problem and user | 20 | Primary user: a housing-register intake caseworker. Public Ombudsman application-handling complaints and related government assessment guidance motivate clear evidence/status handling. No claimed market size or measured delay reduction. |
| AI at the core | 20 | One trained RF estimates additional intake review; actual sklearn probabilities and reconciled Tree SHAP; held-out RF recall 72.9% versus checklist 91.7%. No external LLM inference. |
| Working product | 25 | Applicant submits → same SQLite record in admin → real assessment → SHAP → reasoned human action → applicant status. Retry keys, concurrent submissions, reload and process restart are tested. Exact browser results are in the remediation report. |
| Business and scale | 20 | Proposed buyer: local-authority housing service or housing association intake team. Proposed shadow pilot and second-customer implementation below; pricing and costs are hypotheses, no sales/customers. |
| Responsibility and trust | 15 | Synthetic provenance; original data/model untouched; missed validation target, subgroup FNs and proxy limits visible; no-score/uncertainty/input-range human handoff; no production auth or real housing fairness claim. |

## Spoken pitch

Housing intake caseworkers need to understand incomplete or unclear applications and give applicants a traceable next step. HABITAT AI connects the applicant and caseworker views around the same saved record. Document declarations, the model recommendation and the caseworker’s action stay distinct.

The core is a genuinely trained Random Forest with actual SHAP explanations. Its held-out synthetic accuracy is 77.7%, recall 72.9% and AUC 0.819. The transparent checklist catches more positive labels, so we do not present the model as automatically superior. Uncertainty escalation increases extra-review routing from 37.0% to 57.3%, leaving 12 misses among 128 remaining cases rather than 26 among 189; that is a workload/error trade-off on different simulated populations, not measured housing improvement.

We show the working application, then the failure cases. Original validation routing recall is 84.7%, below 90%. Reaching 90.8% on validation would route 73.7% of cases to extra review, beyond a provisional 70% ceiling that still needs buyer agreement. Group false-negative rates differ materially, and identical paired predictions cannot rule out proxies. The system recommends review; people retain responsibility for every housing decision.

Our proposed buyer is an intake team in a local authority or housing association. The first proposed pilot is four weeks of supervised shadow review, initially synthetic and only later using appropriately governed expert-labelled records after necessary validation. Compare missed-review cases, subgroup errors, caseworker agreement and handling time with the checklist. No live allocation decisions should depend on it.

A cost illustration assumes 1,000 cases/month, 20 routine minutes each, 10 extra minutes for an assumed 60%, £25/hour, £100 infrastructure and £299 software: **£11.23 per application**. It is not a measured saving or validated price. A second customer would need reviewed local intake definitions, authenticated tenant/role isolation, a valid completeness measurement and new workload/fairness evaluation. We have not recruited customers or demonstrated production readiness.

## Inspectable proof

- [README and sources](../README.md)
- [Two-minute click path](DEMO_CHECKLIST.md)
- [Model card](MODEL_CARD.md)
- [Final remediation report and test boundaries](V7_FINAL_REMEDIATION_REPORT.md)
- [Validation-only frontier](../reports/v7-validation-policy-investigation.json)
- [Actual subgroup/case-mix investigation](../reports/v7-fairness-input-investigation.json)

Team member names and a genuine recorded video remain to be supplied by the human team. Codex assisted development and verification; that does not constitute housing-policy validation.
