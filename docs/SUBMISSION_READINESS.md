# V6 submission readiness

The tested synthetic local workflow passes end to end. No critical core-workflow defect was observed. This is not an operational housing service, and the standalone browser suite is not green.

| Check | Status | Evidence |
|---|---|---|
| Applicant submission → administrator → RF → SHAP → review → applicant | PASS | Actual browser refs DEMO-41a21175 / DEMO-cd4ec01f; screenshots and integration audit |
| Multiple applications, refresh, backend restart | PASS | SQLite session associations and saved history; v6-integrity.json |
| Backend/API suite | PASS | 101 tests, 15 dependency warnings |
| Frontend lint/types/production build | PASS | reports/v6-*.txt |
| Data/model/report preservation and no leakage | PASS | Read-only v6-ml-audit.json and v6-integrity.json |
| Standalone Playwright browser execution | FAIL | Five Chrome launch failures before assertions; request-only test passes |
| Mobile viewport matrix, axe, full accessibility audit | NOT TESTED | Browser-launch limitation |
| Validation recall ≥90% target | FAIL | 84.7% validation routing recall; original model retained |
| Real-world housing performance / production security / deployment | NOT TESTED | Synthetic local prototype; no auth/RBAC or legal allocation engine |

Full evidence, exact routes, modified files and commands: [FINAL_INTEGRATION_AUDIT.md](FINAL_INTEGRATION_AUDIT.md).
