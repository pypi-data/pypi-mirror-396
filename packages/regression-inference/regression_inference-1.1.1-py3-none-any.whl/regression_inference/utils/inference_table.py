import numpy as np
from typing import List

def _inference_table(model) -> List[dict[str: float]]:

    stat, model_stat = (
        ("t_statistic", model.t_stat_coefficient)
        if model.model_type == "ols" else
        ("z_statistic", model.z_stat_coefficient)
        if model.model_type == "mle" else
        ValueError("Unknown model type")
    )
    return [
    {
        "feature": feature,
        'coefficient': (np.round(coefficient,4) if abs(coefficient) > 0.0001 else np.format_float_scientific(coefficient, precision=2)),
        'std_error': (np.round(se,4) if abs(se) > 0.0001 else np.format_float_scientific(se, precision=2)),
        f'{stat}': np.round(statistic, 4),
        'P>|t|': f'{p:.3f}',
        f'ci_low_{model.alpha}': (np.round(low,3) if abs(low) > 0.0001 else np.format_float_scientific(low, precision=2)),
        f'ci_high_{model.alpha}': (np.round(high,3) if abs(high) > 0.0001 else np.format_float_scientific(high, precision=2)),

    }
    for feature, coefficient, se, statistic, p, low, high in
    zip(
        model.feature_names,
        model.theta,
        model.std_error_coefficient,
        model_stat,
        model.p_value_coefficient,
        model.ci_low,
        model.ci_high
    )
]