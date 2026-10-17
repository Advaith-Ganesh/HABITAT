"""Reproduce missing-feature failure without changing the production artifact."""

import json
from ml.predict import predict
from ml.common import save_json

result = predict({})
assert result["requires_review"] and result["failure"] == "KeyError"
save_json(
    "reports/failure_case.json",
    {
        "trigger": "Missing model features in an internal inference request. Public API rejects malformed cases before inference.",
        "actual_result": result,
    },
)
print(json.dumps(result, indent=2))
