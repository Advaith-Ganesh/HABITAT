# Final GitHub README showcase report

18 October 2026 · Advaith-Ganesh/HABITAT · Documentation and presentation only.

## Scope and authorship

The README now introduces the actual product and human creators above the fold, walks through the connected V7 workflow, presents stored ML evidence, and explains responsible-AI boundaries, architecture, reproducibility, Mac startup and the proposed business pilot. Original branding is retained. Team names and 60/20/20 allocation come from the human-supplied showcase brief; the allocation is self-reported, not commit statistics. Detailed contributor roles were not invented. The exact requested Codex disclosure is retained. Git author settings and historical authorship were not changed.

## Changed files

| Files | Purpose |
|---|---|
| [README.md](../README.md) | Public project showcase, human attribution, verified results, real screenshots and honest limits |
| [charts/generate.py](charts/generate.py) | Reproducible static Matplotlib SVG generation, read-only report inputs; no model import, training or evaluation |
| [charts/model-comparison.svg](charts/model-comparison.svg), [charts/confusion-matrix.svg](charts/confusion-matrix.svg) | Full four-metric checklist comparison and all held-out classification outcomes |
| [charts/uncertainty-workload.svg](charts/uncertainty-workload.svg), [charts/validation-tradeoff.svg](charts/validation-tradeoff.svg) | Separate held-out safeguard workload and validation-only policy decision |
| [charts/fairness-fnr.svg](charts/fairness-fnr.svg), [charts/dataset-split.svg](charts/dataset-split.svg) | Group errors with denominators and original dataset partition counts |
| [charts/team-contributions.svg](charts/team-contributions.svg) | Human-supplied self-reported allocation, not evaluation data |
| [charts/sources.json](charts/sources.json) | Exact plotted values, source SHA-256s and rendered SVG hashes |
| [screenshots/v7-showcase-human-review.png](screenshots/v7-showcase-human-review.png) | Additional unedited screenshot of the actual running V7 Human Review history, same `DEMO-b38e22c9` case |
| [validate_showcase.py](validate_showcase.py), [showcase-validation.json](showcase-validation.json) | Repeatable links, anchors, SVG and protected-input checks |
| [showcase-existing-readme-validation.json](showcase-existing-readme-validation.json) | Existing V7 README validator result for the new README, saved separately to retain historical V7 evidence |
| This report | Scope, provenance, verification and limits |

Existing V7 applicant, overview, assessment/SHAP and fairness screenshots are referenced unchanged. Assessment and SHAP share one genuine screenshot because the real screen presents them together. No fake screen, deployment URL, video, customer, testimonial or savings claim was added.

## Chart sources

| Figure | Stored source | Population / validation |
|---|---|---|
| Model comparison | [model_comparison.json](../reports/model_comparison.json) | Same 300 held-out cases; all accuracy, precision, recall and F1 values; checklist’s higher recall visible |
| Confusion matrix | [evaluation.json](../reports/evaluation.json) | `[[163,41],[26,70]]`, 300 cases / 96 positives; recomputed metric arithmetic agrees with stored report |
| Uncertainty workload | [v5-safeguard.json](../reports/v5-safeguard.json) | 111/300 versus 172/300 extra-review routing; remaining errors use 189 and 128 denominators |
| Fairness FNR | [fairness.json](../reports/fairness.json) | A:14/41, B:3/32, C:9/23 positive cases; total group sizes 130/102/68; no causal or real-world fairness claim |
| Dataset split | [splits.json](../reports/splits.json), [CSV partitions](../data/splits/train.csv) | Counts 1,400/300/300 checked against actual CSV row counts; separate paired fixture not included |
| Validation trade-off | [v7-validation-policy-investigation.json](../reports/v7-validation-policy-investigation.json) | Validation only, 300 cases / 98 positives; active 84.69% recall, candidate90.82% and73.67% workload; provisional70% capacity remains an assumption |
| Team allocation | Human-supplied request, 18 October 2026 | 60% Advaith Ganesh,20% Abdul Malik,20% Ishaant Verma; not independently audited or inferred from commits |

Figures use navy, teal, slate and muted amber. Metric bars start at zero, rates use percentage units, direct labels retain counts/denominators, and SVG uses a responsive viewBox without scripts, external images or fonts. Sources and material limitations appear beside each figure in the README. No ML evaluation artifact is modified.

## Verification results

| Executed check | Result |
|---|---|
| Existing README validator | **PASS:**58 exact-case local assets/links and5 bash examples parsed; historical result restored byte-for-byte |
| Extended showcase validator | **PASS:**84 local links/fragments across README and this report,7 safe SVGs,10 protected artifact hashes; documentation-only tracked diff |
| Chart validation | **PASS:**all plotted values read from saved reports; both benchmark series checked against confusion-matrix arithmetic; split counts checked against CSVs; repeated generation is byte-reproducible |
| Chart visual inspection | **PASS:**all7 figures inspected as rendered PNGs; fixed a clipped candidate label and converted the confusion matrix into pure vector cells |
| GitHub Markdown API | **PASS:**GitHub GFM render returned HTTP200; no placeholder renderer used |
| Python tests rerun for this documentation task | **PASS:**111 tests,15 dependency deprecation warnings,2.09s |
| ESLint / TypeScript / production build rerun | **PASS** |
| Runtime/data/model/evaluation preservation | **PASS:**all existing non-documentation tracked files match V7 publication82d4588; all10 protected SHA-256s match; no application, API or SHAP change |
| Browser tests | **PASS historical V7 Linux evidence:**9 passed,0 skipped on[final source run39076409671](https://github.com/Advaith-Ganesh/HABITAT/actions/runs/39076409671); not rerun locally for unchanged runtime |
| GitHub page visual verification | Pending publication to a preview branch; result will be finalized after inspection |

Validation scripts resolve local targets case-sensitively and check Markdown fragments against headings. The original README validator also parses shell examples without executing them. Startup scripts and commands were exercised in V7; this task reran the Python suite and frontend checks/build, but did not reinstall Python/Node or replay a fresh Mac installation. Remote-link uptime is not monitored. Local URLs are labelled as local; no video or public app URL is fabricated.

## Remaining limits

The original validation routing-recall target remains **FAIL:84.69% versus90%**. Real-world fairness and production housing use remain unestablished. The existing local macOS standalone Chromium launch restriction is unchanged; green Linux browser evidence is reported separately. No hosted product or genuine video URL was supplied. Automated checks and browser inspection are bounded documentation checks, not a full accessibility certification.
