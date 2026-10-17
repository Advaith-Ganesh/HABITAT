"""Verify the preserved model without training; publish hash-bound verification metadata."""

from datetime import datetime, timezone
import hashlib
from scripts.audit_v2 import main
from ml.safeguard import measure
from ml.common import ROOT, save_json, EVALUATION_INPUTS


def run():
    main("reports/v5-ml-audit.json")
    save_json("reports/v5-safeguard.json", measure())
    paths = EVALUATION_INPUTS
    save_json(
        "reports/evaluation_verification.json",
        {
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "method": "Read-only recomputation from the saved model and preserved held-out data; no retraining.",
            "original_evaluation_created_at": None,
            "artifact_hashes": {
                p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths
            },
        },
    )


if __name__ == "__main__":
    run()
