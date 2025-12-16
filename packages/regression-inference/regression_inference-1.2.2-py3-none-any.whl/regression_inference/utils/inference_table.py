import numpy as np
from typing import List

def _inference_table(model) -> List[dict[str: float]]:

    stat, model_stat = (
        ("t_statistic", model.t_stat_coefficient)
        if model.model_type == "ols" else
        ("z_statistic", model.z_stat_coefficient)
        if model.model_type in ["mle", "multinomial", "ordinal"] else
        ValueError("Unknown model type")
    )

    feature_names = model.feature_names

    if model.model_type == "multinomial":
        
        return _inference_table_multinomial(model, stat, model_stat)
    
    if model.model_type == "ordinal":

        p = len(model.feature_names)
        remainder = model.theta.shape[0] - p

        cutpoint_names = [f"{i}:{i+1}" for i in range(remainder)]

        feature_names = np.concatenate([
            np.array(model.feature_names),
            np.array(cutpoint_names)
    ])

    return [
        {
            "feature": feature,
            'coefficient': _outputFormatting(coefficient),
            'std_error': _outputFormatting(se),
            f'{stat}': np.round(statistic, 4),
            'P>|t|': f'{p:.3f}',
            f'ci_low_{model.alpha}': _outputFormatting(low),
            f'ci_high_{model.alpha}': _outputFormatting(high),
        }
    for feature, coefficient, se, statistic, p, low, high in
    zip(
        feature_names,
        model.theta,
        model.std_error_coefficient,
        model_stat,
        model.p_value_coefficient,
        model.ci_low,
        model.ci_high
    )
]

def _inference_table_multinomial(model, stat_name: str, model_stat: np.ndarray) -> List[dict]:

    results = []
    n_features = model.theta.shape[0]
    n_classes = model.theta.shape[1]  
    class_labels = [f"Class_{model.y_classes[i+1]}" for i in range(n_classes)]

    for class_idx, class_label in enumerate(class_labels):

        for feature_idx, feature_label in enumerate(model.feature_names):

            results.append({
                "feature": feature_label,
                "class": class_label,
                'coefficient': _outputFormatting(model.theta[feature_idx, class_idx]),
                'std_error': _outputFormatting(model.std_error_coefficient[feature_idx, class_idx]),
                f'{stat_name}': np.round(model_stat[feature_idx, class_idx], 4),
                'P>|z|': f'{model.p_value_coefficient[feature_idx, class_idx]:.3f}',
                f'ci_low_{model.alpha}': _outputFormatting(model.ci_low[feature_idx, class_idx]),
                f'ci_high_{model.alpha}': _outputFormatting(model.ci_high[feature_idx, class_idx]),
            })
    
    return results


def _outputFormatting(value: float) -> str:

    if abs(value) > 0.0001:
        return str(np.round(value, 4))
    else:
        return np.format_float_scientific(value, precision=2)