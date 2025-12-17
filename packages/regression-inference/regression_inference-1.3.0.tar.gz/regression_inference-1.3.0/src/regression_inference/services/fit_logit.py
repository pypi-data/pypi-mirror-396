import numpy as np
import warnings
from scipy.stats import norm

COND_THRESHOLD = 1e10
PROB_CLIP_MIN = 1e-15
PROB_CLIP_MAX = 1 - 1e-15

def sigmoid(z: np.ndarray) -> np.ndarray:
    
    return np.where(
        z >= 0,
        1 / (1 + np.exp(-z)),
        np.exp(z) / (1 + np.exp(z))
    )

def internal_logit(model, max_iter: int, tol: float) -> None:

    model.theta = np.zeros(model.X.shape[1])

    converged = fit_gradient(model, max_iter, tol)

    if not converged:
        conv_warn(max_iter)

    if np.max(np.abs(model.theta)) > 10:
        separation_warn(np.max(np.abs(model.theta)))

    model.probabilities, H = (
        predict_prob(model.X, model.theta)
    )

    model.predictions = (
        (model.probabilities >= 0.5).astype(int)
    )

    model.classification_accuracy = (
        np.mean(model.predictions == model.y)
    )

    try:
        model.xtWx_inv = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        raise ValueError("Failed to compute covariance matrix at convergence.")
    
    cond = np.linalg.cond(H)
    if cond > COND_THRESHOLD:
        cond_warn(cond) 

    model.intercept, model.coefficients = (
        model.theta[0],
        model.theta[1:]
    )

    model_params(model)



def fit_gradient(model, max_iter: int, tol: float) -> bool:

    for _ in range(max_iter):

        z = model.X @ model.theta

        mu = (
            np.clip(sigmoid(z), PROB_CLIP_MIN, PROB_CLIP_MAX)
        )

        gradient = (
            model.X.T @ (mu - model.y)
        )

        W = (
            mu * (1 - mu)
        )

        H = (
            model.X.T @ (W[:, np.newaxis] * model.X)
        )
        
        try:
            H_inv = np.linalg.inv(H)
        except np.linalg.LinAlgError:
            raise ValueError(
                "\nHessian matrix is singular. This typically indicates:\n"
                "- Perfect separation in the data\n"
                "- Perfect multicollinearity between features\n"
                "- Insufficient observations\n"
                "- Constant or duplicate columns in X"
        )

        theta_new = (
            model.theta - H_inv @ gradient
        )

        if np.max(np.abs(theta_new - model.theta)) < tol:
            model.theta = theta_new
            return True
        
        model.theta = theta_new
    
    return False


def predict_prob(X: np.ndarray, theta: np.ndarray):

    z = (
        X @ theta
    )

    mu = (
        np.clip(sigmoid(z), PROB_CLIP_MIN, PROB_CLIP_MAX)
    )

    W = (
        mu * (1 - mu)
    )

    H = (
        X.T @ (W[:, np.newaxis] * X)
    )

    return mu, H


def model_params(model) -> None:

    y_hat_prob = model.probabilities

    model.residuals = (
        np.sign(model.y - y_hat_prob) * np.sqrt(-2 * (model.y * np.log(y_hat_prob) + 
        (1 - model.y) * np.log(1 - y_hat_prob)))
    )

    model.log_likelihood = (
        np.sum(model.y * np.log(y_hat_prob) + (1 - model.y) * np.log(1 - y_hat_prob))
    )

    model.deviance = (
        -2 * model.log_likelihood
    )

    y_bar = (
        np.clip(np.mean(model.y), PROB_CLIP_MIN, PROB_CLIP_MAX)
    )
   
    model.null_log_likelihood = (
        np.sum(model.y * np.log(y_bar) + (1 - model.y) * np.log(1 - y_bar))
    )

    model.null_deviance = (
        -2 * model.null_log_likelihood
    )

    n, k = model.X.shape

    model.aic = (
        -2 * model.log_likelihood + 2 * k
    )

    model.bic = (
        -2 * model.log_likelihood + k * np.log(n)
    )

    model.pseudo_r_squared = (
        1 - (model.log_likelihood / model.null_log_likelihood)
    )

    model.lr_statistic = (
        -2 * (model.null_log_likelihood - model.log_likelihood)
    )

    model.variance_coefficient = model.xtWx_inv

    model.std_error_coefficient = (
        np.sqrt(np.diag(model.variance_coefficient))
    )

    model.z_stat_coefficient = (
        model.theta / model.std_error_coefficient
    )

    model.p_value_coefficient = (
        2 * (1 - norm.cdf(abs(model.z_stat_coefficient)))
    )

    z_crit = (
        norm.ppf(1 - model.alpha / 2)
    )

    model.ci_low, model.ci_high = (
        model.theta - z_crit * model.std_error_coefficient, 
        model.theta + z_crit * model.std_error_coefficient
    )


def cond_warn(cond: float):
    warnings.warn(
        f"\nHessian matrix is ill-conditioned (cond={cond:.2e}).\n"
        f"Results may be unreliable. Consider:\n"
        f"- Removing collinear features\n"
        f"- Scaling features\n",
        UserWarning,
        stacklevel=5
    )

def conv_warn(max_iter: int):
    warnings.warn(
        f"\nOptimization did not converge after {max_iter} iterations.\n"
        f"Consider:\n"
        f"- Increasing max_iter\n"
        f"- Adjusting tolerance\n"
        f"- Scaling features\n"
        f"- Checking for separation issues\n",
        UserWarning,
        stacklevel=5
    )

def separation_warn(max_coef: float):
    warnings.warn(
        f"\nLarge coefficients detected (max |θ| > {max_coef:.2f}).\n"
        f"This may indicate separation in the data:\n"
        f"- Perfect or quasi-complete separation\n"
        f"- Classes are linearly separable\n"
        f"- Standard errors may be unreliable\n",
        UserWarning,
        stacklevel=5
    )