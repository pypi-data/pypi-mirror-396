import numpy as np
import warnings
from scipy.optimize import minimize
from scipy.stats import norm

PROB_CLIP_MIN = 1e-15
PROB_CLIP_MAX = 1 - 1e-15

# TODO - Solve convergence error
# TODO - Proper standard errors

# IMPLEMENTED - Correct coefficients 


def _internal_ordinal_logit(model, max_iter: int, tol: float) -> None:
     
    n_samples, model.n_features = model.X.shape
    model.n_classes = len(np.unique(model.y))
    
    if model.n_classes <= 2:
        raise ValueError(
            "Multinomial logit requires 3+ classes. "
            "Use LogisticRegression() for 2 classes."
    )
    
    model.y_classes = np.unique(model.y)
    model.y_encoded = np.searchsorted(model.y_classes, model.y)

    converged = ordinal_fit(model, model.y_encoded, max_iter, tol)

    if not converged.success:
        _conv_warn(max_iter, converged.message)

    y_enc = _ordinal_postfit(model)  
    _model_params(model, y_enc)



def ordinal_fit(model, y, max_iter, tol):

    model.X = np.atleast_2d(model.X)
    n, p = model.X.shape
    J = model.n_classes - 1

    start = np.zeros(p + J)
    start[p:] = np.linspace(-1, 1, J)

    res = minimize(
        _negativeLL,
        start,
        args=(model.X, y, model.n_classes),
        method="BFGS",
        options={"maxiter": max_iter, "gtol": tol}
    )

    model.coefficients = res.x[:p]
    model.alpha_cutpoints = np.sort(res.x[p:])
    model.xtWx_inv = res.hess_inv
    
    # KEEP
    model.theta_cutpoints = np.empty_like(model.alpha_cutpoints)
    model.theta_cutpoints[0] = model.alpha_cutpoints[0]
    model.theta_cutpoints[1:] = np.log(np.diff(model.alpha_cutpoints))
    model.theta = np.concatenate([model.coefficients, model.theta_cutpoints])

    return res


def _ordinal_postfit(model):

    model.probabilities = _predict_prob(
        model.X,
        model.coefficients,
        model.alpha_cutpoints,
        model.n_classes
    )
    model.predictions = np.argmax(model.probabilities, axis=1)
    model.classification_accuracy = np.mean(
        model.predictions == model.y_encoded
    )
    n = len(model.y_encoded)
    Y_onehot = np.zeros((n, model.n_classes))
    Y_onehot[np.arange(n), model.y_encoded] = 1

    return Y_onehot


def _negativeLL(params, X, y, n_classes):

    X = np.atleast_2d(X)
    n, p = X.shape
    J = n_classes - 1

    beta = params[:p]
    tau  = np.sort(params[p:])  
    xb = X @ beta

    def F(z):
        return 1 / (1 + np.exp(-np.clip(z, -700, 700)))

    cdf = np.zeros((n, J))
    for j in range(J):
        cdf[:, j] = F(tau[j] - xb)

    probs = np.zeros((n, n_classes))
    probs[:, 0] = cdf[:, 0]

    for j in range(1, J):
        probs[:, j] = cdf[:, j] - cdf[:, j-1]

    probs[:, J] = 1 - cdf[:, J-1]
    probs = np.clip(probs, PROB_CLIP_MIN, PROB_CLIP_MAX)

    return -np.sum(np.log(probs[np.arange(n), y]))


def _predict_prob(X, beta, alpha, n_classes):

    n = X.shape[0]
    J = len(alpha)
    
    cumulative = np.zeros((n, J))
    
    for j in range(J):
        eta = alpha[j] - X @ beta
        cumulative[:, j] = 1 / (1 + np.exp(-np.clip(eta, -700, 700)))
        
    categorical_pr = np.zeros((n, n_classes))
    categorical_pr[:, 0] = cumulative[:, 0]
        
    for j in range(1, J):
        categorical_pr[:, j] = cumulative[:, j] - cumulative[:, j-1]

    categorical_pr[:, J] = 1 - cumulative[:, J-1]
            
    categorical_pr = np.clip(categorical_pr, PROB_CLIP_MIN, PROB_CLIP_MAX)
    categorical_pr /= categorical_pr.sum(axis=1, keepdims=True)
            
    return categorical_pr


def _model_params(model, y_enc: np.ndarray):

    y_hat_prob = model.probabilities
    y_hat_prob = np.clip(y_hat_prob, PROB_CLIP_MIN, PROB_CLIP_MAX)
    
    model.log_likelihood = np.sum(y_enc * np.log(y_hat_prob))
    model.deviance = -2 * model.log_likelihood
    
    n_samples, n_classes = y_enc.shape
    class_probs = np.mean(y_enc, axis=0)
    class_probs = np.clip(class_probs, PROB_CLIP_MIN, PROB_CLIP_MAX)

    model.null_log_likelihood = np.sum(y_enc * np.log(class_probs))
    model.null_deviance = -2 * model.null_log_likelihood

    n_params = (model.n_features + (model.n_classes - 1))
    model.aic = -2 * model.log_likelihood + 2 * n_params
    model.bic = -2 * model.log_likelihood + n_params * np.log(n_samples)
    model.pseudo_r_squared = 1 - (model.log_likelihood / model.null_log_likelihood)
    model.lr_statistic = -2 * (model.null_log_likelihood - model.log_likelihood)

    model.variance_coefficient = model.xtWx_inv
    std_errors = np.sqrt(np.maximum(np.diag(model.variance_coefficient), 1e-20))
    params = np.concatenate([model.coefficients, model.alpha_cutpoints]) #theta_cutpoints
    model.std_error_coefficient = std_errors
    model.z_stat_coefficient = params / std_errors
    model.p_value_coefficient = 2 * (1 - norm.cdf(np.abs(model.z_stat_coefficient)))
    z_crit = norm.ppf(1 - model.alpha / 2)
    #params = np.concatenate([model.coefficients, model.alpha_cutpoints]) # theta_cutpoints
    model.ci_low = params - z_crit * std_errors
    model.ci_high = params + z_crit * std_errors

    predicted_class = np.argmax(y_hat_prob, axis=1)
    actual_class = model.y_encoded
    model.residuals = (actual_class != predicted_class).astype(float)


def _conv_warn(max_iter: int, message: str = ""):
    warnings.warn(
        f"\nOptimization did not converge after {max_iter} iterations.\n"
        f"Optimizer message: {message}\n"
        f"Consider:\n"
        f"- Increasing max_iter\n"
        f"- Adjusting tolerance\n"
        f"- Scaling features\n"
        f"- Checking for separation issues\n"
        f"- Ensuring sufficient samples per class\n",
        UserWarning,
        stacklevel=5
)
