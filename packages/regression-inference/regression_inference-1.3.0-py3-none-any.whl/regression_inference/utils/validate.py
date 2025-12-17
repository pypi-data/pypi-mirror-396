import numpy as np 

def validate(X: np.ndarray, y: np.ndarray, alpha: float, model_type: str):

    if X is None or y is None:
        raise ValueError("X and y cannot be None")
    
    X_array = np.asarray(X, dtype=float)
    y_array = np.asarray(y, dtype=float)
    
    if X_array.size == 0 or y_array.size == 0:
        raise ValueError("X and y cannot be empty")
    
    if len(X_array.shape) != 2:
        raise ValueError(f"X must be 2D, got shape {X_array.shape}")
    
    if len(y_array.shape) != 1:
        if len(y_array.shape) == 2 and y_array.shape[1] == 1:
            y_array = y_array.flatten()
        else:
            raise ValueError(f"y must be 1D, got shape {y_array.shape}")
    
    if X_array.shape[0] != y_array.shape[0]:
        raise ValueError(
            f"X and y must have same number of observations. "
            f"Got X: {X_array.shape[0]}, y: {y_array.shape[0]}"
    )
    
    if X_array.shape[0] <= X_array.shape[1]:
        raise ValueError(
            f"Insufficient observations. Need n > k, "
            f"got n={X_array.shape[0]}, k={X_array.shape[1]}"
    )
    
    if not (0 < alpha < 1):
        raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")
    
    if np.any(~np.isfinite(X_array)):
        raise ValueError("X contains NaN or infinite values")
    
    if np.any(~np.isfinite(y_array)):
        raise ValueError("y contains NaN or infinite values")
    
    if model_type == 'logit':
        unique_values = np.unique(y_array)
        
        if not np.all(np.isin(y_array, [0, 1])):
            raise ValueError(
                f"For logistic regression, y must contain only 0 and 1. "
                f"Found unique values: {unique_values}"
        )
        if len(unique_values) < 2:
            raise ValueError(
                f"y must have at least 2 classes for logistic regression. "
                f"Found only: {unique_values}"
        )
        class_0_count = np.sum(y_array == 0)
        class_1_count = np.sum(y_array == 1)
        if class_0_count < 2 or class_1_count < 2:
            import warnings
            warnings.warn(
                f"Very imbalanced classes detected: "
                f"class 0: {class_0_count}, class 1: {class_1_count}. "
                f"Model may fail to converge or produce unreliable estimates.",
                UserWarning
        )
        
    return (
        X_array,
        y_array
)