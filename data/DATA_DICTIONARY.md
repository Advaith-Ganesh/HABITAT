# Data dictionary

All records are fictional. GBP units are demo assumptions. Source columns:

| Column | Definition and role |
|---|---|
| `application_id` | Unique fictional intake identifier (HAB prefix). Not a model feature. |
| `scenario_id` | Related household family identifier. Used only for group-isolated splitting. |
| `household_size` | Household people, integer 1–7; context only. |
| `household_members` | Same people count as household_size; retained as a documented alias; excluded from model. |
| `monthly_income` | Fictional GBP per month, 300–5,000. Context only; excluded from model and labels. |
| `monthly_housing_cost` | Fictional GBP per month. Context only. |
| `current_bedrooms` | Bedroom count, integer 0–4. Context only. |
| `housing_situation` | stable / temporary / unclear. Model input. |
| `housing_insecurity_reported` | Boolean 0/1, derived from non-stable situation. Model input; correlated with situation. |
| `overcrowding_indicator` | Fictional 0/1 marker for household size >4. Context only; not a statutory overcrowding test. |
| `missing_document_count` | Count of absent income/identity/housing evidence, integer 0–3. Model input. |
| `income_document_available` | 0/1 evidence availability. Model input. |
| `identity_document_available` | 0/1 evidence availability. Model input. |
| `housing_evidence_available` | 0/1 evidence availability. Model input. |
| `accessibility_support_requested` | Random 0/1 support request. Context only; excluded to avoid penalising a request. |
| `specialist_support_requested` | 0/1 fictional specialist caseworker review need. Model input; may be sensitive/proxy in practice and requires governance. |
| `conflicting_information` | 0/1 fictional inconsistency flag. Model input. |
| `application_completeness_score` | Fictional score 5–100 percent. Model input. |
| `reported_residency_context` | reported / unclear; audit/context only, excluded from model and labels. |
| `synthetic_audit_group` | Audit A/B/C, arbitrary simulated audit categories. Audit only. |
| `age_band` | 18–34 / 35–64 / 65+; randomly simulated age group. Audit/context only, excluded. |
| `case_review_required` | Target 0 routine human workflow / 1 additional human review. Never a feature. |

The counterfactual file adds pair_id (integer 0–199); both members retain identical task fields. Source generation and input API ranges differ deliberately: API validation supports wider illustrative household ranges, which are outside the training distribution. Such cases need human scrutiny.
