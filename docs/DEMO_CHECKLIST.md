# V6 applicant–administrator demonstration

Run `bash scripts/start_backend.sh` and `bash scripts/start_frontend.sh` from the project root. Open http://127.0.0.1:5173. Use synthetic values only.

1. **Apply for Housing:** Household members 4; Continue. Monthly income £1800, default £600 cost and Stable housing; Continue. Uncheck Income evidence available (2/3 = 66.7%); Continue. Leave support/conflict off; Continue. Confirm all values are synthetic; Submit application.
2. **My Applications:** keep the unique reference. It shows Awaiting assessment and Income evidence missing. Use Start another application to submit a second structured case; both references remain in the SQLite-backed session list after refresh.
3. Keep a second same-origin tab on **Administrator → Overview** during submission. Counts refetch from SQLite after mutation notifications. Switch to **Applications**, search the reference, Open → Open AI assessment → **Run AI Assessment**.
4. The first payload produced **53.0595%** in V6. Displayed rounding is 53.1%; it is probability of extra review, never housing approval. The separate document percentage is 66.7%. Inspect the saved model version/timestamp and genuine SHAP chart; input changes can produce other scores. Reassessment before completion saves a new timestamp and the same score for identical inputs.
5. **Fairness & Sandbox:** show measured performance, subgroup counts/error rates and the unresolved validation target. Run group analysis; Rerun 200 paired comparisons. Paired equality on an excluded label does not prove fairness. Compare HAB-0023 by Audit A → Audit B (same score), then conflict 0 → 1 (observed 14.9% → 65.1%); the stored case is untouched.
6. **Human Review:** select the submitted reference, Request more evidence, enter a meaningful synthetic reason, Record review action, Confirm review action. Applicant → My Applications displays Additional information requested and the actual reason. Human escalation and continued review also keep a case pending.
7. Complete review with a reason and confirm. Applicant displays Administrative review completed; this is not housing approval. Reload both portals, restart the backend using the same DB path and refresh again. Status, history, assessment and both applications persist.
8. Optional resilience demonstration: stop the backend, Refresh status, show the service error, restart and Retry. Do not retry an uncertain submission blindly: no idempotency key exists.

The current verified UI has three applicant links, five administrator tabs, full labels/icons, and a small Sandbox · Synthetic Data disclosure. Production authentication, document uploads, legal eligibility and actual housing allocation are outside this sandbox.

Read [the integration audit](FINAL_INTEGRATION_AUDIT.md) for PASS / FAIL / NOT TESTED results. Standalone Chrome launch fails in this environment; do not call its browser suite green.
