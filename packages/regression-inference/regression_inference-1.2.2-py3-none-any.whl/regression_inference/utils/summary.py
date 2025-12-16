import numpy as np

def summary(*args):

    col_width, col_span, models = (
        15,
        30,
        list(args)
    )
    for i, model in enumerate(models):
        if model.theta is None:
            raise ValueError(f"Error: Model {i+1} is not fitted.")
    
    if len(set(m.model_type for m in models)) > 1:
        raise ValueError("Error: Cannot stack different model types.")

    format_length = col_span + (len(models)*col_width)

    header = (
        f"{'='*format_length}\n"
        f"{(
            "OLS Regression Results"
            if models[0].model_type == "ols" else
            "Logistic Regression Results"
            if models[0].model_type == "mle" else
            "Multinomial Regression Results"
            if models[0].model_type == "multinomial" else
            "Ordinal Regression Results"
            if models[0].model_type == "ordinal" else
            ValueError(f"Unknown model type: {models[0].model_type}")
            )}\n"
        f"{'-'*format_length}\n"
        f"{'Dependent:':<{col_span}}" + "".join(f"{m.target:>{col_width}}" for m in models) + "\n"
        f"{'-'*format_length}\n"
    )

    feature_names = model.feature_names

    if model.model_type == "ordinal":

        p = len(model.feature_names)
        remainder = model.theta.shape[0] - p

        cutpoint_names = [f"{i}:{i+1}" for i in range(remainder)]

        feature_names = np.concatenate([
            np.array(model.feature_names),
            np.array(cutpoint_names)
    ])

    all_features = []
    for model in models:
        for feature in feature_names:
            if feature not in all_features:
                all_features.append(feature)

    rows = []

    if not models[0].model_type == "multinomial":
        for feature in all_features:
            coef_row = f"{feature:<{col_span}}"
            se_row = " " * col_span

            for model in models:
                if feature in feature_names:
                    feature_index = list(feature_names).index(feature)
                    coef = model.theta[feature_index]
                    se = model.std_error_coefficient[feature_index]
                    p = model.p_value_coefficient[feature_index]

                    stars = (
                        "***" if p < 0.01 else
                        "**" if p < 0.05 else
                        "*" if p < 0.1 else
                        ""
                    )
                    coef_fmt = (
                        f"{coef:.4f}{stars}"
                        if abs(coef) > 0.0001
                        else f"{coef:.2e}{stars}"
                    )
                    se_fmt = (
                        f"({se:.4f})"
                        if abs(se) > 0.0001
                        else f"({se:.2e})"
                    )
                    coef_row += f"{coef_fmt:>{col_width}}"
                    se_row += f"{se_fmt:>{col_width}}"
                else:
                    coef_row += " " * col_width
                    se_row += " " * col_width

            rows.append(" ")
            rows.append(coef_row)
            rows.append(se_row)
    else:
        J = model.theta.shape[1]  # number of non-reference classes

        for j in range(J):
            
            col_num = int(model.y_classes[j+1])
            rows.append(f"{f"{'Class:':<{col_span}}" + f"{col_num:>{col_width}}"}\n")
           

            for feature in all_features:
                coef_row = f"{feature:<{col_span}}"
                se_row = " " * col_span

                for model in models:
                    i = list(model.feature_names).index(feature)

                    coef = model.theta[i, j]
                    se = model.std_error_coefficient[i, j]
                    p = model.p_value_coefficient[i, j]

                    stars = (
                        "***" if p < 0.01 else
                        "**" if p < 0.05 else
                        "*" if p < 0.1 else
                        ""
                    )
                    coef_fmt = (
                        f"{coef:.4f}{stars}"
                        if abs(coef) > 0.0001
                        else f"{coef:.2e}{stars}"
                    )
                    se_fmt = (
                        f"({se:.4f})"
                        if abs(se) > 0.0001
                        else f"({se:.2e})"
                    )
                    coef_row += f"{coef_fmt:>{col_width}}"
                    se_row += f"{se_fmt:>{col_width}}"

                
                rows.append(coef_row)
                rows.append(se_row)
                rows.append(" ")

            rows.append(f"{'-'*format_length}")


    if model.model_type == "ols":
        stats_lines = [
            ("R-squared", "r_squared"),
            ("Adjusted R-squared", "r_squared_adjusted"),
            ("F Statistic", "f_statistic"),
            ("Observations", lambda m: m.X.shape[0]),
            ("Log Likelihood", "log_likelihood"),
            ("AIC", "aic"),
            ("BIC", "bic"),
            ("TSS", "tss"),
            ("RSS", "rss"),
            ("ESS", "ess"),
            ("MSE", "mse"),
        ]
        
    if model.model_type in ["mle", "multinomial", "ordinal"]:
         stats_lines = [
            ("Accuracy", "classification_accuracy"),
            ("Pseudo R-squared", "pseudo_r_squared"),
            ("LR Statistic", "lr_statistic"),
            ("Observations", lambda m: m.X.shape[0]),
            ("Log Likelihood", "log_likelihood"),
            ("Null Log Likelihood", "null_log_likelihood"),
            ("Deviance", "deviance"),
            ("Null Deviance", "null_deviance"),
            ("AIC", "aic"),
            ("BIC", "bic")
        ]


    stats = f"\n{'-'*format_length}\n"

    for label, attr in stats_lines:
        stat_row = f"{label:<{col_span}}"
        for model in models:
            stat_row += f"{(attr(model) if callable(attr) else getattr(model, attr)):>{col_width}.3f}"
        stats += stat_row + "\n"

    return (
        header +
        "\n".join(rows) + "\n" +
        stats +
        f"{'='*format_length}\n"
        "*p<0.1; **p<0.05; ***p<0.01\n"
    )