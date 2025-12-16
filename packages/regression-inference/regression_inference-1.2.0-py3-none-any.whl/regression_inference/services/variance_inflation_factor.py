import numpy as np

def _variance_inflation_factor(model):

    X = model.X[:,1:]
    n_features, vif = X.shape[1], []

    for i in range(n_features):

        mask = np.ones(n_features, dtype=bool)
        mask[i] = False
        X_j = X[:, i]                                                                        # Target
        X_other_with_intercept = np.column_stack([np.ones(X[:, mask].shape[0]), X[:, mask]]) # Other Features

        # Auxiliary fit
        xtx = X_other_with_intercept.T @ X_other_with_intercept
        theta_aux = np.linalg.solve(xtx, X_other_with_intercept.T @ X_j)
        y_hat_aux = X_other_with_intercept @ theta_aux
        tss_aux = np.sum((X_j - np.mean(X_j))**2)

        if tss_aux < 1e-10:
            vif.append(np.inf)
            continue
        
        rss_aux = np.sum((X_j - y_hat_aux)**2)
        r_squared_aux = 1 - (rss_aux / tss_aux)
        vif.append(1 / (1 - r_squared_aux) if r_squared_aux < 0.9999 else np.inf)

    return ({
        'feature': model.feature_names[1:],
        'VIF': np.round(vif, 4)
    })