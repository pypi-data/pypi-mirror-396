from typing import Optional
from ..utils.input_validator import validate
from .fit_ols import _internal_linear
from .fit_mle import _internal_logit
from .fit_multinomial import _internal_multinomial_logit
from .fit_ordinal import _internal_ordinal_logit
import numpy as np

def _get_featureLabel(X, feature_names):
    '''
    Feature labels are assigned in a hierarchy:

    User defined names -> Pandas column names -> Fallback names.

    The assignment is always in order of the columns from the X array or dataframe
    '''
    return (
        ['const', *feature_names] if feature_names is not None
        else X.columns if hasattr(X, 'columns')
        else ['const', *[f"Feature {i}" for i in range(1,X.shape[1])]]  
    )

def _get_targetLabel(y, target_name):
    '''
    Target label is assigned in a hierarchy:

    User defined name -> Pandas series name -> Fallback name.
    '''
    return (
        target_name if target_name is not None
        else y.name if hasattr(y, 'name')
        else "Dependent"
    )

def _fit(
        model,
        X:              np.ndarray,
        y:              np.ndarray,
        feature_names:  Optional[list[str]],
        target_name:    Optional[str],
        alpha:          float,
        max_iter:       int = 100,
        tol:            float = 1e-8,
        ordinal:        bool = False
    ):

    '''
    Model fit helper for model delegation
    '''

    X_array, y_array = validate(X, y, alpha, model.model_type)
    model.feature_names = _get_featureLabel(X, feature_names)
    model.target = _get_targetLabel(y, target_name)
    model.alpha = alpha
    model.X, model.y = X_array, y_array
    model.degrees_freedom = model.X.shape[0]-model.X.shape[1]

    if model.model_type == "ols":
        _internal_linear(model)

    elif model.model_type == "mle":
        _internal_logit(model, max_iter, tol)

    elif model.model_type == "multinomial":
        _internal_multinomial_logit(model, max_iter, tol)
        
    elif model.model_type == "ordinal":
        _internal_ordinal_logit(model, max_iter, tol)

    else:
        raise ValueError(f"Unknown model_type: {model.model_type}")
    
    return model


