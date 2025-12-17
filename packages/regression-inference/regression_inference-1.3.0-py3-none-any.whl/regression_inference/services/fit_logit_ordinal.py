import numpy as np
import warnings
from scipy.optimize import minimize
from scipy.stats import norm

PROB_CLIP_MIN = 1e-15
PROB_CLIP_MAX = 1 - 1e-15

# TODO - Solve convergence error
# TODO - Improve numerical stability for high dimensional data

'''

adj_cutpoints: bool = False 

    - True:  Model adjacent cutpoint differences for the coefficient and covariance matrix
             Used by statsmodels.api

    - False: Model absolute cumulative cutpoint differences
             Used by MASS:polr (R)

'''

def internal_ordinal_logit(model, adj_cutpoints: bool, max_iter: int, tol: float) -> None:
     
    _, model.n_features = model.X.shape

    model.n_classes = len(np.unique(model.y))
    
    if model.n_classes <= 2:
        raise ValueError(
            "Multinomial logit requires 3+ classes. "
            "Use LogisticRegression() for 2 classes."
    )
    
    model.y_classes = (
        np.unique(model.y)
    )

    model.y_encoded = (
        np.searchsorted(model.y_classes, model.y)
    )

    converged = (
        fit(model, adj_cutpoints, model.y_encoded, max_iter, tol)
    )

    if not converged.success:
        conv_warn(max_iter, converged.message)

    y_enc = postfit(model)  

    model_params(model, adj_cutpoints, y_enc)



def fit(model, adj_cutpoints: bool, y: np.ndarray, max_iter: int, tol: float):

    model.X = np.atleast_2d(model.X)

    _, n_features = model.X.shape

    J = model.n_classes - 1

    start = np.zeros(n_features + J)

    start[n_features:] = np.linspace(-1, 1, J)

    res = minimize(
        negativeLL,
        start,
        args=(model.X, y, model.n_classes),
        method="BFGS",
        options={"maxiter": max_iter, "gtol": tol}
    )

    model.coefficients = (
        res.x[:n_features]
    )

    model.alpha_cutpoints = (
        np.sort(res.x[n_features:])
    )

    H = numerical_hessian(
        negativeLL,
        res.x,
        args=(model.X, y, model.n_classes)
    )

    model.xtWx_inv = np.linalg.inv(H)
    
    model.theta_cutpoints = np.empty_like(model.alpha_cutpoints)

    model.theta_cutpoints[0] = model.alpha_cutpoints[0]

    model.theta_cutpoints[1:] = np.log(np.diff(model.alpha_cutpoints))

    model.theta = (
        np.concatenate([model.coefficients, model.theta_cutpoints])
        if adj_cutpoints else
        np.concatenate([model.coefficients, model.alpha_cutpoints])
    )

    return res



def negativeLL(params, X, y, n_classes):

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



def numerical_hessian(fun, x0, args=(), eps=1e-5):

    x0 = np.asarray(x0)
    n = x0.size
    H = np.zeros((n, n))

    f0 = fun(x0, *args)

    for i in range(n):
        x_i_plus  = x0.copy()
        x_i_minus = x0.copy()
        x_i_plus[i]  += eps
        x_i_minus[i] -= eps

        f_ip = fun(x_i_plus, *args)
        f_im = fun(x_i_minus, *args)

        H[i, i] = (f_ip - 2 * f0 + f_im) / eps**2

        for j in range(i + 1, n):
            x_pp = x0.copy()
            x_pm = x0.copy()
            x_mp = x0.copy()
            x_mm = x0.copy()

            x_pp[i] += eps; x_pp[j] += eps
            x_pm[i] += eps; x_pm[j] -= eps
            x_mp[i] -= eps; x_mp[j] += eps
            x_mm[i] -= eps; x_mm[j] -= eps

            f_pp = fun(x_pp, *args)
            f_pm = fun(x_pm, *args)
            f_mp = fun(x_mp, *args)
            f_mm = fun(x_mm, *args)

            val = (f_pp - f_pm - f_mp + f_mm) / (4 * eps**2)
            H[i, j] = val
            H[j, i] = val

    return H



def predict(X: np.ndarray, beta: np.ndarray, alpha: float, n_classes: int) -> np.ndarray:

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



def postfit(model) -> np.ndarray:

    model.probabilities = predict(
        model.X,
        model.coefficients,
        model.alpha_cutpoints,
        model.n_classes
    )

    model.predictions = (
        np.argmax(model.probabilities, axis=1)
    )

    model.classification_accuracy = (
        np.mean(model.predictions == model.y_encoded)
    )

    n = len(model.y_encoded)

    y_onehot = np.zeros((n, model.n_classes))

    y_onehot[np.arange(n), model.y_encoded] = 1

    return y_onehot



def model_params(model, adj_cutpoints: bool, y_enc: np.ndarray) -> None:

    y_hat_prob = (
        np.clip(model.probabilities, PROB_CLIP_MIN, PROB_CLIP_MAX)
    )
    
    model.log_likelihood = (
        np.sum(y_enc * np.log(y_hat_prob))
    )

    model.deviance = (
        -2 * model.log_likelihood
    )
    
    n_samples, _ = y_enc.shape

    class_probabilities = (
        np.clip(np.mean(y_enc, axis=0), PROB_CLIP_MIN, PROB_CLIP_MAX)
    )

    model.null_log_likelihood = (
        np.sum(y_enc * np.log(class_probabilities))
    )

    model.null_deviance = (
        -2 * model.null_log_likelihood
    )

    n_params = (
        model.n_features + (model.n_classes - 1)
    )

    model.aic = (
        -2 * model.log_likelihood + 2 * n_params
    )

    model.bic = (
        -2 * model.log_likelihood + n_params * np.log(n_samples)
    )

    model.pseudo_r_squared = (
        1 - (model.log_likelihood / model.null_log_likelihood)
    )

    model.lr_statistic = (
        -2 * (model.null_log_likelihood - model.log_likelihood)
    )

    if adj_cutpoints:
        model.variance_coefficient = transform_covariance(model)
        model.std_error_coefficient = np.sqrt(np.maximum(np.diag(model.variance_coefficient), 1e-20))
    else:
        model.variance_coefficient = model.xtWx_inv
        model.std_error_coefficient = np.sqrt(np.diag(model.variance_coefficient))

    model.z_stat_coefficient = (
        model.theta / model.std_error_coefficient
    )

    model.p_value_coefficient = (
        2 * (1 - norm.cdf(np.abs(model.z_stat_coefficient)))
    )

    z_crit = (
        norm.ppf(1 - model.alpha / 2)
    )

    model.ci_low, model.ci_high = (
        model.theta - z_crit * model.std_error_coefficient,
        model.theta + z_crit * model.std_error_coefficient
    )

    predicted_class = np.argmax(y_hat_prob, axis=1)

    actual_class = model.y_encoded

    model.residuals = (actual_class != predicted_class).astype(float)



def transform_covariance(model) -> np.ndarray:

    beta = model.coefficients
    alpha = model.alpha_cutpoints

    p = len(beta)
    J = len(alpha)
    V = model.xtWx_inv

    dim = p + J
    G = np.zeros((dim, dim))

    G[:p, :p] = np.eye(p)
    G[p, p] = 1.0

    for j in range(1, J):
        denom = alpha[j] - alpha[j - 1]
        G[p + j, p + j]     =  1.0 / denom
        G[p + j, p + j - 1] = -1.0 / denom

    V_theta = G @ V @ G.T
    return V_theta



def conv_warn(max_iter: int, message: str = ""):
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
