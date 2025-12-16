import numpy as np
import warnings
from scipy.optimize import minimize

PROB_CLIP_MIN = 1e-15
PROB_CLIP_MAX = 1 - 1e-15

# TODO - Solve convergence error
# TODO - Proper standard errors

# IMPLEMENTED - Correct coefficients 

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


def ordinal_postfit(model):

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




