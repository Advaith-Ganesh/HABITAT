"""Score-cutoff investigation using validation only. Never loads final-test data."""
import hashlib
import numpy as np
import pandas as pd
from ml.common import ROOT, FEATURES
from ml.predict import artifacts


def investigate_validation(target=0.90, capacity=0.70):
    pipe, cfg = artifacts()
    path = ROOT / 'data/splits/validation.csv'
    val = pd.read_csv(path)
    scores = pipe.predict_proba(val[FEATURES])[:, 1]
    positive = val.case_review_required.to_numpy().astype(bool)
    frontier = []
    for cutoff in sorted(set(scores), reverse=True):
        routed = scores >= cutoff
        frontier.append({'cutoff': float(cutoff),
                         'uncertainty_margin': float(max(0, cfg['threshold']-cutoff)),
                         'routing_recall': float(routed[positive].mean()),
                         'extra_review_rate': float(routed.mean()),
                         'extra_review_count': int(routed.sum()),
                         'missed_positive_count': int((positive & ~routed).sum())})
    target_policies = [r for r in frontier if r['routing_recall'] >= target]
    feasible = [r for r in target_policies if r['extra_review_rate'] <= capacity]
    original = scores >= cfg['threshold']-cfg['uncertainty_margin']
    return {'selection_data': 'validation only; final test not loaded by this analysis',
            'model_retrained': False, 'active_policy_changed': False,
            'target': target, 'provisional_workload_ceiling': capacity,
            'ceiling_status': 'Operating assumption declared before exploration; not a validated buyer capacity or universal definition of reasonable workload.',
            'original': {'threshold': cfg['threshold'], 'uncertainty_margin': cfg['uncertainty_margin'],
                         'routing_recall': float(original[positive].mean()),
                         'extra_review_rate': float(original.mean())},
            'minimum_workload_target_policy': min(target_policies, key=lambda r:r['extra_review_rate']),
            'feasible_within_ceiling': feasible,
            'decision': 'Retain original policy. No monotone score cutoff meets both the recall target and provisional capacity ceiling. A larger review budget could support the documented validation candidate; this requires an operating decision, not a claim that 90% was achieved by the active policy.',
            'candidate_test_evaluation': 'NOT PERFORMED: no replacement policy selected; candidate was not evaluated on final test.',
            'validation_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'model_sha256': hashlib.sha256((ROOT/'models/habitat_review_model.joblib').read_bytes()).hexdigest(),
            'active_config_sha256': hashlib.sha256((ROOT/'models/config.json').read_bytes()).hexdigest(),
            'frontier': frontier}
