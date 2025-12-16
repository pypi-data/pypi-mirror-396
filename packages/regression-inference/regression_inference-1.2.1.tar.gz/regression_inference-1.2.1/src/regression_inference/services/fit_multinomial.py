import numpy as np
import warnings
from scipy.stats import norm

COND_THRESHOLD = 1e10
PROB_CLIP_MIN = 1e-15
PROB_CLIP_MAX = 1 - 1e-15

def _softmax(Z: np.ndarray) -> np.ndarray:

    Z_stable = Z - np.max(Z, axis=1, keepdims=True)
    exp_Z = np.exp(np.clip(Z_stable, -700, 700))
    return exp_Z / np.sum(exp_Z, axis=1, keepdims=True)


def _internal_multinomial_logit(model, max_iter: int, tol: float) -> None:
     
    n_samples, model.n_features = model.X.shape
    model.n_classes = len(np.unique(model.y))
    
    if model.n_classes <= 2:
        raise ValueError(
            "Multinomial logit requires 3+ classes. "
            "Use LogisticRegression() for 2 classes."
    )
    
    model.y_classes = np.unique(model.y)
    model.y_encoded = np.searchsorted(model.y_classes, model.y)
    Y_onehot = np.zeros((n_samples, model.n_classes))
    Y_onehot[np.arange(n_samples), model.y_encoded] = 1

    _standard_fit(model, Y_onehot, n_samples, max_iter, tol)



def _standard_fit(model, y_enc: np.ndarray, n_samples: int, max_iter: int, tol: float) -> None:

    p = model.n_features
    J = model.n_classes - 1
    Y = y_enc[:, 1:] 
    theta = np.zeros((p, J))

    for _ in range(max_iter):

        Z = model.X @ theta
        Z_full = np.column_stack([np.zeros(n_samples), Z])

        P = _softmax(Z_full)

        Pj = P[:, 1:] 
        grad = model.X.T @ (Y - Pj)         
        grad_flat = grad.flatten(order="F")

        H = _standard_hessian(model.X, P)

        try:
            step = np.linalg.solve(H, grad_flat)
        except np.linalg.LinAlgError:
            step = np.linalg.pinv(H) @ grad_flat

        theta_new = theta + step.reshape(p, J, order="F")

        if np.max(np.abs(theta_new - theta)) < tol:
            break

        theta = theta_new

    model.theta = theta
    model.probabilities = _predict_prob(model.X, model.theta)
    model.predictions = np.argmax(model.probabilities, axis=1)
    model.classification_accuracy = np.mean(model.predictions == model.y_encoded)

    H = _standard_hessian(model.X, model.probabilities)

    cond = np.linalg.cond(H)
    if cond > COND_THRESHOLD:
        _cond_warn(cond)

    try:
        model.xtWx_inv = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        warnings.warn(
            "Hessian is singular, using pseudo-inverse. Standard errors may be unreliable.",
            UserWarning
        )
        model.xtWx_inv = np.linalg.pinv(H)

    model.intercept = model.theta[0, :]
    model.coefficients = model.theta[1:, :]
    _model_params(model, y_enc)



def _standard_hessian(X: np.ndarray, probs: np.ndarray) -> np.ndarray:

    n_samples, n_features = X.shape
    n_classes = probs.shape[1]
    n_alt = n_classes - 1 

    H = np.zeros((n_features * n_alt, n_features * n_alt))

    for i in range(n_samples):

        p = probs[i, 1:] 
        V = np.diag(p) - np.outer(p, p)  
        Xi = X[i][:, None]    
        XiXiT = Xi @ Xi.T       
        H += np.kron(V, XiXiT)  

    return H



def _predict_prob(X: np.ndarray, theta: np.ndarray) -> np.ndarray:
    
    n_samples = X.shape[0]
    n_classes = theta.shape[1] + 1
    Z = X @ theta
    Z_full = np.column_stack([np.zeros(n_samples), Z])
    return _softmax(Z_full)



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

    n_params = (model.theta.size)
    model.aic = -2 * model.log_likelihood + 2 * n_params
    model.bic = -2 * model.log_likelihood + n_params * np.log(n_samples)
    model.pseudo_r_squared = 1 - (model.log_likelihood / model.null_log_likelihood)
    model.lr_statistic = -2 * (model.null_log_likelihood - model.log_likelihood)

    model.variance_coefficient = model.xtWx_inv
    std_errors = np.sqrt(np.maximum(np.diag(model.variance_coefficient), 1e-20))

    theta_flat = model.theta.flatten(order="F")
    model.std_error_coefficient = std_errors
    model.z_stat_coefficient = theta_flat / std_errors
    model.p_value_coefficient = 2 * (1 - norm.cdf(np.abs(model.z_stat_coefficient)))
    z_crit = norm.ppf(1 - model.alpha / 2)
    #theta_flat = model.theta.flatten(order="F")
    model.ci_low = theta_flat - z_crit * std_errors
    model.ci_high = theta_flat + z_crit * std_errors
    shape = model.theta.shape
    model.std_error_coefficient = model.std_error_coefficient.reshape(shape, order="F")
    model.z_stat_coefficient = model.z_stat_coefficient.reshape(shape, order="F")
    model.p_value_coefficient = model.p_value_coefficient.reshape(shape, order="F")
    model.ci_low = model.ci_low.reshape(shape, order="F")
    model.ci_high = model.ci_high.reshape(shape, order="F")

    predicted_class = np.argmax(y_hat_prob, axis=1)
    model.residuals = (model.y_encoded != predicted_class).astype(float)



def _cond_warn(cond: float):
    warnings.warn(
        f"\nHessian matrix is ill-conditioned (cond={cond:.2e}).\n"
        f"Results may be unreliable. Consider:\n"
        f"- Removing collinear features\n"
        f"- Scaling features\n"
        f"- Increasing sample size per class\n",
        UserWarning,
        stacklevel=5
)

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

def _separation_warn(max_coef: float):
    warnings.warn(
        f"\nLarge coefficients detected (max |θ| = {max_coef:.2f}).\n"
        f"This may indicate separation in the data:\n"
        f"- Perfect or quasi-complete separation\n"
        f"- Classes are linearly separable\n"
        f"- Standard errors may be unreliable\n",
        UserWarning,
        stacklevel=5
)
