"""Reproduce V7 investigations without retraining or changing canonical model/data/reports."""
import hashlib
from scripts.audit_v2 import main
from ml.common import ROOT, EVALUATION_INPUTS, save_json
from ml.validation_policy import investigate_validation
from ml.audit_v7 import investigate


def run():
    before = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in EVALUATION_INPUTS}
    # Freeze the validation-only decision before any held-out descriptive analysis.
    save_json('reports/v7-validation-policy-investigation.json', investigate_validation())
    save_json('reports/v7-fairness-input-investigation.json', investigate())
    main('reports/v7-ml-audit.json')
    after = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in EVALUATION_INPUTS}
    assert before == after
    save_json('reports/v7-protected-artifacts.json', {'all_10_unchanged':True,'sha256':after})


if __name__ == '__main__':
    run()
