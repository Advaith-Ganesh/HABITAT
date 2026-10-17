# Displayed-value and interaction audit — V5

A = live persisted database values; B = calculated individual-application values; C = fixed model/dataset evaluation and method configuration; D = explicit business assumptions; E = broken/misleading presentation found and repaired. Constant values in C are legitimate; they must not be randomly altered to look live.

| Active display | Class | Actual source / calculation | V5 finding or action |
|---|---|---|---|
| Total submitted | A | SQLite application rows, `/api/dashboard.applications` | Verified13→14 after submission |
| Awaiting assessment | A | `status=unassessed` count | Verified0→1→0 |
| Human-review queue | A | `status=pending` count | Verified5→6→5 |
| Completed reviews | A | `status=resolved` count | Added visible live counter;1→2 |
| Information requests | A | Pending rows whose latest human event requests evidence | Verified0→1→0 |
| Recent activity, references, timestamps, reasons | A | Actual latest SQLite events; UK-local formatted time | No fabricated growth series or customers |
| Table/result counts and pagination | A/B | Filtered API rows, six rows/page, current/total pages | Six is page-size configuration, not a customer metric |
| Household, income, housing circumstances | A | Saved validated payload | No real personal records used in verification |
| Application status / outstanding request | A | DB status plus latest human event | List previously showed generic pending; now exposes the real request |
| Documentation percentage | B | Present declared categories / actual requirement count ×100 | All8 flag combinations tested;2/3=66.7% |
| Missing/present category names | B | Saved flags + three demo requirement labels | No statutory sufficiency claim |
| New submission intake-completeness input | B | Same document ratio sent to existing model feature | Historic values untouched; not independently validated |
| Additional-review probability/category | B | Actual saved Pipeline `predict_proba`, configured threshold | Exact match to direct inference; no forced differences |
| Uncertainty flag/human recommendation | B/C | Actual score within validation-selected margin | Live new case53.1%, uncertaintytrue |
| Base value / each SHAP contribution | B | Real TreeExplainer, transformed features aggregated by original input | Sum checked against score; zero/error does not become a fake chart |
| Explanation text | B | Top actual contributions, input values and attribution signs | No causes or invented legal reasons |
| Individual two-case comparison | B | Two real predictions/SHAP runs with one changed input | Saved case unchanged; irrelevant-vs-relevant distinction explicit |
| Accuracy, precision, recall, F1, matrix, AUC | C | Preserved `reports/evaluation.json`, independently recomputed | Labelled held-out test set; fixed until artifacts change |
| Model/version/trees/training/validation/test counts | C | Loaded model/config plus actual split CSV sizes | Versionrf-1.0;180 fitted trees;1400/300/300 |
| Evaluation date | C | `evaluation_verification.json.verified_at`, bound to10 artifact hashes | Newly shown honest recomputation date; original creation timestamp unknown |
| Baseline results | C | Saved/recomputed deterministic checklist | Higher checklist recall disclosed |
| Checklist70-point cutoff / ≥1missing condition | C | Existing deterministic baseline method | Method settings, not learned legal rules |
| FPR/FNR/selection/accuracy by group | C | Fairlearn held-out labels/predictions | Group denominators visible; no universal fairness claim |
| Group counts, positive/negative supports | C | Actual held-out group subsets |130/102/68, positives41/32/23 |
| Concern threshold10pp and minimum20 per class | C | Existing descriptive fairness heuristic | Exposed as method configuration; not a confidence interval |
| Pair count/row count/example count/differences | C | Separate generated paired fixture and real predictions | Removed repeated literal400/200/5 in active display text |
| Proxy correlation | C | Actual one-hot audit membership/numeric-input Pearson calculation | Low correlation cannot rule out combined proxies |
| Safeguard errors/counts/workload | C | `ml.safeguard.measure()` from untouched test scores | Added67/300 before any escalation; no test tuning |
| Dataset2000 /1000families /22columns /70-15-15 | C | Public CSV, dictionary, splits metadata, reproducible generator | Separate400-row audit fixture is not training data |
| Prices£299/£999;1000volume,20min,£25/hour,60%human,£100infra | D | Explicit hypothetical business inputs | No actual sales, revenue or measured savings claimed |
| Estimated£5.40per case | D | (1000×20/60×25×.6+100+299)/1000, rounded | Formula and assumptions visible |
| Form1–5steps, field ranges, graph0–100% ticks | B/C | Form structure/schema, chart scale and formatting | Interface/method constants, not fabricated statistics |
| Reassessment clears human request | E | Existing inference status assignment could override caseworker queue | Fixed; regression verifies routine prediction cannot clear pending follow-up |
| SHAP loading message | E | During calculation it could ask to assess an already assessed case | Explicit calculation/unavailable states; no placeholder chart |
| Paired rerun label | E | First dynamic-label edit exposed literal expression during smoke | Fixed to actual computed pair count; rerun verified in browser |
| Mocked live totals or predictions | E | Source/inference/cross-tab comparison | None found in active functional views |

## Interaction and refresh contract

Successful submissions and human/model actions persist first, then trigger same-tab refetch. A same-origin storage revision event refreshes other demo tabs; visibility return also refreshes. No fixed-interval polling. If storage is unavailable, retain your reference and use Refresh. Applicant pages do not fetch SHAP or fairness diagnostics; demo APIs remain unauthenticated and must not be exposed as production access control.

Search/filter/pagination, native input validation, submission, assessment/reassessment, mandatory notes, confirmation, persisted applicant status, group rerun, paired rerun, group selection, pair selection, one-input comparisons, tooltips, theme and download endpoints have explicit data sources. Old source components retained for safety are not extra active portal routes. The only active sidebar routes are3 applicant and5 administrator items.
