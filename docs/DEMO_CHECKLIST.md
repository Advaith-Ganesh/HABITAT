# Two-minute applicant-to-caseworker product walkthrough

Start `bash scripts/start_backend.sh` and `bash scripts/start_frontend.sh` from the repository root. Open http://127.0.0.1:5173. This is a local synthetic sandbox; portal switching is not authentication.

1. **0:00–0:25 — Applicant / Apply for Housing:** household 4, income £1800, Stable housing, missing Income evidence. On Support & clarification keep conflict/specialist off. Applicants no longer estimate a completeness percentage. Check and submit synthetic values. Point out the real reference and **2-of-3 =66.7% document completeness**, separate from the unavailable training-time feature.
2. **0:25–0:50 — Administrator / Applications:** search that reference, Open → Open AI assessment → Run AI Assessment. The V7.1 input-compatibility check routes the new application to human review with no score or SHAP. For genuine saved-model/SHAP inspection, separately open an existing numeric-input record such as `DEMO-SEED-001`; this does not turn its historical feature into a validated measure for new applications.
3. **0:50–1:15 — Human Review:** Request more evidence with a reason, Record and Confirm. Switch to applicant and show the actual reason/status. Complete administrative review with a second reason; reload to demonstrate persistence. This never allocates housing.
4. **1:15–1:45 — Fairness & Sandbox:** show RF versus checklist, the unmet validation target and workload trade-off. Run group analysis; inspect false-negative counts and case mix. Rerun 200 paired comparisons. Say: “Identical paired predictions do not establish absence of proxy discrimination.”
5. **1:45–2:00 — Honest failure and value:** explain that missing artifacts produce a no-score human fallback, SHAP failures show errors rather than invented reasons, and out-of-training inputs require human handling. The automated browser suite fault-injects explanation failure and lost submission responses. A real backend outage/recovery and process restart were also tested.

Optional extended walkthrough: submit the same unconfirmed request again after a lost response; its stable UUID key returns the same reference. Start another application after confirmed success to create a genuinely new request. Native invalid-input errors are announced, mobile labels remain visible and scrollable audit tables accept keyboard focus.

The independent sandbox scenarios use DEMO-SEED-001 through DEMO-SEED-012 and are independent of held-out data. To reset, stop the backend and run `.venv/bin/python -m scripts.reset_sandbox`; an existing sandbox is backed up first. Do not reset historical evidence.

[Final verified results and exact limitations](V7_FINAL_REMEDIATION_REPORT.md) · [Judging pitch](PITCH_V7.md).
