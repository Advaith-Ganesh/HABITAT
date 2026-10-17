# HABITAT synthetic intake benchmark

**Entirely synthetic; not real housing applicants**

Generated synthetic benchmark — no personal data — not representative of any national housing applicant population.

Version 1.0.0 · creation/reference date 2026-10-17 · seed 42 · 2,000 records / 1,000 scenario families.

## Purpose and provenance
Demonstrate intake-review routing, supervised learning, explanation and auditing in a local hackathon sandbox. No external applicant records, names, addresses, identifiers or demographic data were ingested. "Audit A/B/C" are arbitrary synthetic categories; they represent no ethnicity or nationality. Age bands are randomly simulated and audit-only. No ethnicity is inferred from names.

## Sampling and family structure
A NumPy default_rng(42) generates 1,000 households, each with two related intake variants. Family-shared household size (uniform integers 1–7), income (uniform £300–£5,000/month), housing situation (60% stable, 25% temporary, 15% unclear) and audit category (45% A, 35% B, 20% C) create dependence. Other values are generated independently conditional on these circumstances. Costs are 20–85% of income; these ranges are illustrative only. Both family variants remain in one partition. No sampling claim about any national population is made.

## Honest label construction
The fictional intake label is a Bernoulli draw with probability sigmoid(z):

z = -3.4 + 1.25 × missing_document_count + 2.5 × conflicting_information + 1.9 × specialist_support_requested + .045 × (100 − completeness) + 1.4 × (housing_situation == unclear) + Normal(0, .65).

Then independently flip the label with probability .025. Evidence absence probabilities are .16, .10 and .20 for income, identity and housing evidence. Completeness = clip(100 − 18 × missing_count − Normal(8,12), 5,100), rounded to one decimal place. Conflict probability .13; specialist request .16; accessibility request .18. Specialist review is a fictional workflow need, never a disadvantage or housing allocation rule. Protected/sensitive context is not used in this label.

Monthly income is never an eligibility threshold. Label 0 means routine human review workflow; label 1 means additional human review. Neither means approved, rejected or eligible.

## Splitting and leakage
Group-stratified family split uses the sum of the two family labels (0/1/2) as a stratification class, with fixed seed 42: 700 families training, 150 validation, 150 testing. Exact row sizes: 1,400/300/300. IDs and scenario IDs are disjoint. Train-only imputation and one-hot encoding live inside an sklearn Pipeline. The label, IDs, synthetic audit attributes, age, residency context and income are excluded from inputs. Evaluation metadata includes hashes, class counts and isolation checks. Within-input duplicates can occur by chance because some fields are discrete; family membership, not feature uniqueness, defines independence.

## Separate paired audit
200 separate pairs / 400 rows are generated with seed 4242. Exact model-input duplicates of source rows are excluded, and CF-prefixed scenario/application IDs are assigned. Members of each pair differ only in synthetic_audit_group. These records are never used for training, threshold selection or model selection. Labels on these records are unused by the paired audit. Equality is expected because group membership is excluded; this is not evidence against proxy discrimination.

## Limitations and intended uses
Use for reproducible software demonstrations, classroom audits and method debugging. Synthetic labels and inputs share generator assumptions: good agreement is partly circular. Label noise is simulated, not measured expert disagreement. The benchmark does not establish model usefulness beyond its generator. No causal, statutory, national representativeness or universal fairness claim is supported. Unsuitable for real housing allocation, applicant ranking, rejection, statutory eligibility, demographic inference or real-world validation. These are responsible-use instructions; CC0 reuse terms remain as stated in LICENSE.md.

## Reproduction
From repository root: `.venv/bin/python -m data.generate_dataset`. This regenerates byte-identical CSVs with pinned dependencies; tests compare the complete source CSV to a fresh in-memory generation. Run `bash scripts/reproduce.sh` to regenerate splits, train, evaluate and test. Data hashes are recorded in reports/splits.json.

## V4 portal use

The original 2,000 records and split files were preserved byte-for-byte; no retraining occurred. New demo submissions record the same three document-availability flags. Documentation completeness is present/3×100; it is a UI/backend declaration summary, not a legal eligibility test or target probability. The new form derives the existing application_completeness_score input from these declarations. Historical synthetic intake completeness may differ and is not overwritten. This new mapping has not been externally validated.
