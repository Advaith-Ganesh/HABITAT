"""Training-only range/category checks; these cannot establish full distribution alignment."""
from functools import lru_cache
import hashlib
import numpy as np
import pandas as pd
from ml.common import ROOT, FEATURES, NUMERIC


@lru_cache(maxsize=1)
def training_profile():
    path = ROOT / 'data/splits/train.csv'
    train = pd.read_csv(path)
    return {
        'training_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'feature_order': FEATURES,
        'numeric_ranges': {k: {'min': float(train[k].min()), 'max': float(train[k].max())} for k in NUMERIC},
        'housing_categories': sorted(train.housing_situation.unique().tolist()),
        'limitation': 'Training-range/category checks only. Novel combinations, measurement mismatch and real-world distribution shift may pass these checks.',
    }


def check_inputs(record):
    profile = training_profile()
    warnings = []
    imputed = []
    for field in FEATURES:
        value = record[field]
        if pd.isna(value):
            imputed.append(field)
            warnings.append(f'{field}: missing value uses the training-fitted imputer; human verification required.')
        elif field == 'housing_situation':
            if value not in profile['housing_categories']:
                warnings.append(f'{field}: category absent from training; human verification required.')
        else:
            bounds = profile['numeric_ranges'][field]
            if not np.isfinite(float(value)) or not bounds['min'] <= float(value) <= bounds['max']:
                warnings.append(f"{field}: outside observed training range [{bounds['min']}, {bounds['max']}]; human verification required.")
    return {'warnings': warnings, 'imputed_features': imputed, 'out_of_distribution': bool(warnings), 'scope': profile['limitation']}
