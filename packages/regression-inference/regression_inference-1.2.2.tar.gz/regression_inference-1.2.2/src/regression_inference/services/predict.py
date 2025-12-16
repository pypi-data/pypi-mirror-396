import numpy as np    
from scipy.stats import t as t_dist, norm

PROB_CLIP_MIN = 1e-15
PROB_CLIP_MAX = 1 - 1e-15

def _predict(model, X, alpha, return_table):

    X = np.asarray(X, dtype=float)

    '''
    Predictor for LogisticRegression()
    '''
    def _sigmoid(z):
        return np.where(
            z >= 0,
            1 / (1 + np.exp(-z)),
            np.exp(z) / (1 + np.exp(z))
    )


    '''
    Predictor for MultinomialRegression()
    '''
    def _softmax(Z: np.ndarray) -> np.ndarray:
        Z_stable = Z - np.max(Z, axis=1, keepdims=True)
        exp_Z = np.exp(np.clip(Z_stable, -700, 700))
        return exp_Z / np.sum(exp_Z, axis=1, keepdims=True)
    
    
    '''
    Predictor for OrdinalRegression()
    '''
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


    '''
    Prediction as integer
    '''
    if not return_table:

        return (

            X @ model.coefficients + model.intercept
            if model.model_type == "ols" else

            _sigmoid(X @ model.coefficients + model.intercept)
            if model.model_type == "mle" else

            _softmax(
                np.column_stack([
                    np.zeros(X.shape[0]),
                    np.asarray(X, dtype=float) @ model.coefficients + model.intercept
                ])
            )
            if model.model_type == "multinomial" else

            _predict_prob(
                np.atleast_2d(X),
                model.coefficients,
                model.alpha_cutpoints,
                model.n_classes
            )
            if model.model_type == "ordinal" else

            ValueError(f"Unknown model type: {model.model_type}")
        )


    '''
    Tabular Predictions shared configurations
    '''
    # Ordinal has no intercept
    if not model.model_type == "ordinal":
        prediction_features = {
                name: f'{value_at.item():.2f}'
                for name, value_at in zip(model.feature_names[1:], X[0])
        }

        X = np.hstack([np.ones((X.shape[0], 1)), X])

    # Only Linear and base Logit 
    if not model.model_type in ["multinomial", "ordinal"]:
        prediction = X @ model.theta
        se_prediction = (
            np.sqrt((X @ model.variance_coefficient @ X.T)).item()
        )


    '''
    Tabular Least Squares Predictions
    '''
    if model.model_type == "ols":
                
        t_critical = t_dist.ppf(1 - alpha/2, model.degrees_freedom)

        ci_low, ci_high = (
            (prediction - t_critical * se_prediction),
            (prediction + t_critical * se_prediction)
        )
        t_stat = (
            prediction / se_prediction
            if se_prediction > 0
            else np.inf
        )
        p = 2 * (1 - t_dist.cdf(abs(t_stat), model.degrees_freedom))

        return ({
            "features": [prediction_features],
            "prediction": [np.round(prediction.item(), 4)],
            "std_error": [np.round(se_prediction,4)],
            "t_statistic": [np.round(t_stat.item(),4)],
            "P>|t|": [f"{p.item():.3f}"],
            f"ci_low_{alpha}": [np.round(ci_low.item(), 4)],
            f"ci_high_{alpha}": [np.round(ci_high.item(), 4)],
        })
    

    '''
    Tabular base Logit Predictions
    '''
    if model.model_type == "mle":

        prediction_prob = _sigmoid(prediction)
        z_critical = norm.ppf(1 - alpha/2)

        ci_low_z, ci_high_z = (
            (prediction - z_critical * se_prediction),
            (prediction + z_critical * se_prediction)
        )
        ci_low_prob, ci_high_prob = (
            _sigmoid(ci_low_z),
            _sigmoid(ci_high_z)
        )

        z_stat = (
            prediction / se_prediction
            if se_prediction > 0
            else np.inf
        )
        p = 2 * (1 - norm.cdf(abs(z_stat)))

        return ({
            "features": [prediction_features],
            "prediction_prob": [np.round(prediction_prob.item(), 4)],
            "prediction_class": [int(prediction_prob.item() >= 0.5)],
            "std_error": [np.round(se_prediction, 4)],
            "z_statistic": [np.round(z_stat.item(), 4)],
            "P>|z|": [f"{p.item():.3f}"],
            f"ci_low_{alpha}": [np.round(ci_low_prob.item(), 4)],
            f"ci_high_{alpha}": [np.round(ci_high_prob.item(), 4)],
        })


    '''
    Tabular Multinomial Logit Predictions
    '''
    if model.model_type == "multinomial":
        
        x = X[0]
        p, J = model.theta.shape
        z_crit = norm.ppf(1 - alpha / 2)

        ''' 'J' Linear Predictors -> Add Reference Class -> Convert To Probabilities '''
        prediction = x @ model.theta        
        eta_full = np.r_[0.0, prediction]     
        prediction_prob = _softmax(eta_full[None, :])[0]

        classes = []
        for j in range(J):

            '''Compute inference for J reference classes'''

            idx = slice(j*p, (j+1)*p)
            Vj = model.xtWx_inv[idx, idx]  # Cov block

            se_eta = np.sqrt(x @ Vj @ x)

            ''' Log odds relative to reference class'''

            ci_low_eta, ci_high_eta = (     
                prediction[j] - z_crit * se_eta,
                prediction[j] + z_crit * se_eta
            )
            eta_low, eta_high = (
                eta_full.copy(),
                eta_full.copy()
            )
            eta_low[j+1], eta_high[j+1] = (
                ci_low_eta,
                ci_high_eta
            )
            p_low, p_high = (
                _softmax(eta_low[None, :])[0][j+1],
                _softmax(eta_high[None, :])[0][j+1]
            )

            z_stat = prediction[j] / se_eta if se_eta > 0 else np.inf
            p_val = 2 * (1 - norm.cdf(abs(z_stat)))

            classes.append({
                "multinomial_class": model.y_classes[j+1],
                "features": prediction_features,
                "prediction_prob": np.round(prediction_prob[j+1], 4),
                "prediction_linear": np.round(prediction[j], 4),
                "std_error": np.round(se_eta, 4),
                "z_statistic": np.round(z_stat, 4),
                "P>|z|": f"{p_val:.3f}",
                f"ci_low_{alpha}": np.round(p_low, 4),
                f"ci_high_{alpha}": np.round(p_high, 4),
            })

        return classes
    

    '''
    Tabular Ordinal Logit Predictions
    '''
    if model.model_type == "ordinal":

        X = np.atleast_2d(X)

        prediction_features = {
            name: f'{value_at.item():.2f}'
            for name, value_at in zip(model.feature_names, X[0])
        }

        probs = _predict_prob(
            X,
            model.coefficients,
            model.alpha_cutpoints,
            model.n_classes
        )

        results = []
        for i in range(X.shape[0]):
            p_i = probs[i]
            pred_class = int(np.argmax(p_i))
            expected = float(np.dot(p_i, np.arange(model.n_classes)))
            cumulative = np.cumsum(p_i)

            results.append({
                "features": [prediction_features],
                "prediction_class": pred_class,
                "prediction_expected": round(expected, 4),
                "prediction_probabilities": np.round(p_i, 4).tolist(),
                "cumulative_probabilities": np.round(cumulative, 4).tolist(),
            })

        return results
