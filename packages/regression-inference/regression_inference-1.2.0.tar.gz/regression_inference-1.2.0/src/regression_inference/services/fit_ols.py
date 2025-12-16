import numpy as np
import warnings
from scipy.stats import t as t_dist

NUMERICAL_ZERO = 1e-15
CONDITION_THRESHOLD = 1e10

def _internal_linear(model):
    xtx = model.X.T @ model.X
    model.theta, model.xtx_inv = _fit_ols(xtx, model.X, model.y)

    cond = np.linalg.cond(xtx)
    if cond > CONDITION_THRESHOLD:
        _raise_cond(cond)

    model.intercept, model.coefficients = model.theta[0], model.theta[1:]
    model.predictions = model.X @ model.theta
    model.residuals = model.y - model.predictions
    _model_params(model)

    
def _fit_ols(xtx: np.ndarray, X: np.ndarray, y: np.ndarray):
    """Solve closed form OLS using Cholesky decomposition."""
    try:
        L = np.linalg.cholesky(xtx)
        theta = np.linalg.solve(L.T, np.linalg.solve(L, X.T @ y))
        I = np.eye(xtx.shape[0])
        xtx_inv = np.linalg.solve(L.T, np.linalg.solve(L, I))
        return theta, xtx_inv
    except np.linalg.LinAlgError:
        raise ValueError(
            "\nMatrix X'X is not positive definite. This typically indicates:\n"
            "- Perfect multicollinearity between features\n"
            "- Insufficient observations (n < k)\n"
            "- Constant or duplicate columns in X"
    )


def _model_params(model):

    y_bar = np.mean(model.y)

    model.rss = model.residuals @ model.residuals
    model.ess = np.sum((model.predictions - y_bar)**2)
    model.tss = np.sum((model.y - y_bar)**2)
    model.mse = model.rss / model.degrees_freedom
    model.rmse = np.sqrt(model.mse)

    model.f_statistic = (
        (model.ess / model.coefficients.shape[0]) / model.mse
        if model.coefficients.shape[0] > 0 and model.mse > NUMERICAL_ZERO
        else np.nan
    )
    model.r_squared = (1 - (model.rss / model.tss)
                       if model.tss > NUMERICAL_ZERO
                       else np.nan
    )
    model.r_squared_adjusted = (
        1 - (1 - model.r_squared) * (model.X.shape[0] - 1) / model.degrees_freedom
        if not np.isnan(model.r_squared)
        else np.nan
    )
    model.log_likelihood = (
        -model.X.shape[0]/2 * (np.log(2 * np.pi) + np.log(model.rss / model.X.shape[0]) + 1)
        if model.rss > NUMERICAL_ZERO
        else np.inf
    )
    model.aic = (
        -2 * model.log_likelihood + 2 * model.X.shape[1]
        if np.isfinite(model.log_likelihood)
        else np.nan
    )
    model.bic = (
        -2 * model.log_likelihood + model.X.shape[1] * np.log(model.X.shape[0])
        if np.isfinite(model.log_likelihood)
        else np.nan
    )

    model.variance_coefficient = model.mse * model.xtx_inv
    model.std_error_coefficient = np.sqrt(np.diag(model.variance_coefficient))

    model.t_stat_coefficient = (
        model.theta / model.std_error_coefficient
        if model.mse > NUMERICAL_ZERO
        else np.full_like(model.theta, np.nan)
    )
    model.p_value_coefficient = (
        2 * (1 - t_dist.cdf(abs(model.t_stat_coefficient), model.degrees_freedom))
    )
    
    t_crit = t_dist.ppf(1 - model.alpha/2, model.degrees_freedom)
    model.ci_low = model.theta - t_crit * model.std_error_coefficient
    model.ci_high = model.theta + t_crit * model.std_error_coefficient


def _raise_cond(cond: float):
    warnings.warn(
            f"\nMatrix is ill-conditioned (cond={cond:.2e}).\n"
            f"Results may be unreliable. Consider:\n"
            f"- Removing collinear features\n"
            f"- Scaling features\n",
            UserWarning,
            stacklevel=5
    )

