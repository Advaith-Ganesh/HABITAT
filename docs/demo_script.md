# Four-minute demo

1. Open the overview. Point out the sandbox ribbon, fictional counts and measured recall. Explain the task: additional human intake review, never eligibility or allocation.
2. Assess a case using fictional defaults. Tick contradictory information and the fictional-values confirmation; submit. Show the real estimated score and Tree SHAP chart. Distinguish attribution from policy evidence.
3. Open Fairness Lab. Read group FNR differences and potential-concern findings. Rerun 200 paired comparisons; explicitly explain why excluded audit inputs should leave predictions equal and why this proves no universal fairness.
4. Open Human Review. Open the submitted DEMO case, enter a meaningful reason and record a human workflow outcome. Show the persisted append-only event history; reload/open the record to verify persistence.
5. Open Model Performance. Compare the checklist's higher recall against the forest's higher accuracy/F1 and lower review rate. Explain the failed validation recall target and the remaining false negatives.
6. Open Policy Packs and the GOV.UK source. Demo rules are fictional assumptions. International profiles are unimplemented placeholders.
7. Download the 2,000-row synthetic CSV, inspect its card and hashes. Open the pilot calculator, change volume/review proportion and show assumptions, not proven savings.

Failure demo: ` .venv/bin/python -m scripts.failure_demo ` reproduces missing-input human fallback without damaging artifacts. Public malformed requests instead receive validation errors. Demo video: TODO (record a real walkthrough).
