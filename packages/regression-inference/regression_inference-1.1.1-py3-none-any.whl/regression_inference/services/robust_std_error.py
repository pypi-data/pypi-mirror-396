import numpy as np
from scipy.stats import t as t_dist, norm

def _robust_se(model, type, apply=False):

    def _sigmoid(z):
        return np.where(
            z >= 0,
            1 / (1 + np.exp(-z)),
            np.exp(z) / (1 + np.exp(z))
    )

    model_type = model.model_type
    X = model.X
    THETA = model.theta
    ALPHA = model.alpha
    DF = model.degrees_freedom
    n, k = X.shape

    if model_type == "ols":
        stat_dist, stat_name = (t_dist, 't')

        XTX_INV = model.xtx_inv
        h = np.sum(X @ XTX_INV * X, axis=1)
        sr = model.residuals.reshape(-1, 1).flatten()**2

    if model_type == "mle":
        
        stat_dist, stat_name = (norm, 'z')
        z = X @ THETA
        mu = _sigmoid(z)
        W = mu * (1 - mu) 
        XTX_INV = model.xtWx_inv
        h = np.sum(X @ XTX_INV * X, axis=1) * W

        # Response residuals != deviance residuals
        response_residuals = model.y - mu
        sr = response_residuals**2
        
    HC_ = {
        "HC0": lambda sr, n_obs, k_regressors, leverage: sr,
        "HC1": lambda sr, n_obs, k_regressors, leverage: (n_obs / (n_obs - k_regressors)) * sr,
        "HC2": lambda sr, n_obs, k_regressors, leverage: sr / (1 - leverage),
        "HC3": lambda sr, n_obs, k_regressors, leverage: sr / ((1 - leverage) ** 2),
    }

    # Compute only the diagonal matrix
    try:
        omega_diagonal = HC_[type](sr, n, k, h)
        X_omega = X * np.sqrt(omega_diagonal)[:, None]           # Multiply each X row by X*(diagonal weights)^(0.5)
        robust_cov = XTX_INV @ (X_omega.T @ X_omega) @ XTX_INV   # Sandwich
        robust_se = np.sqrt(np.diag(robust_cov))                 # Diagonal extract the var-cov
        robust_stat = THETA / robust_se

        if model_type == "ols":
            robust_p = 2 * (1 - stat_dist.cdf(abs(robust_stat), DF))
            crit = stat_dist.ppf(1 - ALPHA/2, DF)

        if model_type == "mle":
            robust_p = 2 * (1 - stat_dist.cdf(abs(robust_stat)))
            crit = stat_dist.ppf(1 - ALPHA/2)

        robust_ci_low = THETA - crit * robust_se
        robust_ci_high = THETA + crit * robust_se

        if apply:
            if model_type == "ols":
                model.t_stat_coefficient = robust_stat
            if model_type == "mle":
                model.z_stat_coefficient = robust_stat

            model.variance_coefficient = robust_cov
            model.std_error_coefficient = robust_se
            model.p_value_coefficient = robust_p
            model.ci_low = robust_ci_low
            model.ci_high = robust_ci_high

        return {
        "feature":              model.feature_names,
        "robust_se":            robust_se,
        f"robust_{stat_name}":  robust_stat,
        "robust_p":             robust_p,
        f"ci_low_{ALPHA}":      robust_ci_low,
        f"ci_high_{ALPHA}":     robust_ci_high,
    }
    
    except KeyError:
        raise ValueError("Select 'HC0', 'HC1', 'HC2', 'HC3'")