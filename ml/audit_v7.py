"""Read-only descriptive investigations. Never selects policies using held-out data."""
import json
from functools import lru_cache
import numpy as np
import pandas as pd
from ml.common import ROOT, FEATURES, NUMERIC
from ml.predict import artifacts
from ml.input_audit import training_profile


@lru_cache(maxsize=1)
def investigate():
    pipe, cfg = artifacts()
    test = pd.read_csv(ROOT / 'data/splits/test.csv')
    score = pipe.predict_proba(test[FEATURES])[:, 1]
    predicted = score >= cfg['threshold']
    uncertain = np.abs(score - cfg['threshold']) <= cfg['uncertainty_margin']
    routed = predicted | uncertain
    y = test.case_review_required.to_numpy().astype(bool)
    groups = []
    for name in sorted(test.synthetic_audit_group.unique()):
        mask = (test.synthetic_audit_group == name).to_numpy()
        positive = mask & y
        fn = positive & ~predicted
        subset = test.loc[mask]
        groups.append({
            'group': name, 'count': int(mask.sum()), 'positive_count': int(positive.sum()),
            'negative_count': int((mask & ~y).sum()), 'positive_rate': float(y[mask].mean()),
            'false_negative_count': int(fn.sum()), 'false_negative_rate': float(fn.sum() / positive.sum()),
            'uncertain_count': int((mask & uncertain).sum()),
            'uncertain_rate': float(uncertain[mask].mean()),
            'extra_review_count': int((mask & routed).sum()),
            'extra_review_rate': float(routed[mask].mean()),
            'routing_missed_positive_count': int((positive & ~routed).sum()),
            'routing_recall': float(routed[positive].mean()),
            'characteristics': {'mean_missing_categories': float(subset.missing_document_count.mean()),
                                'mean_information_completeness': float(subset.application_completeness_score.mean()),
                                'unclear_housing_rate': float((subset.housing_situation == 'unclear').mean()),
                                'conflicting_information_rate': float(subset.conflicting_information.mean()),
                                'specialist_requested_rate': float(subset.specialist_support_requested.mean())},
            'false_negative_characteristics': {'mean_missing_categories': float(test.loc[fn].missing_document_count.mean()),
                                              'mean_information_completeness': float(test.loc[fn].application_completeness_score.mean())} if fn.any() else None,
        })
    train = pd.read_csv(ROOT / 'data/splits/train.csv')
    conditional = []
    for missing, rows in train.groupby('missing_document_count'):
        conditional.append({'missing_categories': int(missing), 'count': len(rows),
                            'training_mean': float(rows.application_completeness_score.mean()),
                            'training_min': float(rows.application_completeness_score.min()),
                            'training_max': float(rows.application_completeness_score.max()),
                            'old_document_mapping': 100 * (3-int(missing))/3})
    saved_fairness = json.loads((ROOT / 'reports/fairness.json').read_text())
    return {
        'method': 'Descriptive held-out group comparison under unchanged original policy; no test-based policy selection.',
        'groups': groups,
        'proxy_correlations': saved_fairness['proxy_correlations'],
        'maximum_absolute_proxy_correlation': saved_fairness['maximum_absolute_proxy_correlation'],
        'warning': 'Subgroup errors differ. Small synthetic samples and case-mix differences do not establish a causal explanation or real-world housing fairness.',
        'paired_warning': 'Identical paired predictions do not establish absence of proxy discrimination.',
        'input_consistency': {'training_profile': training_profile(),
            'training_formula': 'clip(100 - 18 * missing_document_count - Normal(8,12), 5,100), rounded to one decimal',
            'previous_intake_mapping': '100 * present_document_categories / 3',
            'mismatch': 'Document availability and broader information completeness are different constructs. The V6 mapping collapses a noisy continuous training feature into four document percentages.',
            'change': 'V7 separately declares intake information completeness and calculates document completeness from evidence flags. A defensible real-world measurement protocol remains unvalidated.',
            'conditional_training_completeness': conditional,
            'imputation': 'Training-only numeric median; housing most-frequent; unknown categories encoded with handle_unknown=ignore and now escalated by input checks.',
            'encoding_feature_order_verified': list(pipe.feature_names_in_) == FEATURES,
            'training_numeric_medians_match_fitted_imputer': bool(np.allclose(pipe['transform'].named_transformers_['numeric'].statistics_, train[NUMERIC].median().values)),
        },
    }
