from dataclasses import dataclass, field
from typing import Union, ClassVar, Optional
from abc import ABC, abstractmethod
from .services.variance_inflation_factor import _variance_inflation_factor
from .services.robust_std_error import _robust_se
from .services.predict import _predict
from .services.fit import _fit
from .utils.inference_table import _inference_table
from .utils.summary import summary
import numpy as np

@dataclass
class Model(ABC):

    feature_names:          list[str] = field(default_factory=list)
    target:                 Optional[str] = None
    X:                      Optional[np.ndarray] = field(default=None, repr=False)
    y:                      Optional[np.ndarray] = field(default=None, repr=False)
    alpha:                  Optional[float] = None
    theta:                  Optional[np.ndarray] = field(default=None)
    coefficients:           Optional[np.ndarray] = field(default=None)
    intercept:              Optional[float] = None
    predictions:            Optional[np.ndarray] = field(default=None)
    degrees_freedom:        Optional[int] = None
    residuals:              Optional[np.ndarray] = field(default=None, repr=False)
    log_likelihood:         Optional[float] = None
    aic:                    Optional[float] = None
    bic:                    Optional[float] = None
    p_value_coefficient:    Optional[np.ndarray] = field(default=None)
    variance_coefficient:   Optional[np.ndarray] = field(default=None)
    std_error_coefficient:  Optional[np.ndarray] = field(default=None)
    ci_low:                 Optional[np.ndarray] = field(default=None)
    ci_high:                Optional[np.ndarray] = field(default=None)

    frozen:                 bool = field(default=False, repr=False)
    MUTABLE_AFTER_FIT:      ClassVar[frozenset[str]] = frozenset({"feature_names", "target", "frozen"})

    def __str__(self) -> str:
        self._model_is_fitted()
        return summary(self)

    def __setattr__(self, name: str, value) -> None:
        if getattr(self, "frozen", False) and name not in self.MUTABLE_AFTER_FIT:
            raise AttributeError(
                f"\nCannot modify '{name}' after model is fitted. "
                f"Model attributes are read-only once fit() is called."
            )
        super().__setattr__(name, value)
        
    @property
    @abstractmethod
    def model_type(self) -> str:
        pass

    @property
    def is_fitted(self) -> bool:
        return self.theta is not None
    
    def _model_is_fitted(self) -> None:
        if not self.is_fitted:
            raise ValueError("Model is not fitted. Call 'fit' with arguments before using this method.")
        
    def _freeze(self) -> None:
        self.frozen = True

    def _post_fit_processing(self, cov_type: Optional[str]) -> None:
        if cov_type:
            _robust_se(self, type=cov_type, apply=True)
        self._freeze()
    
    @abstractmethod
    def fit(
        self,
        X:             np.ndarray,
        y:             np.ndarray,
        feature_names: Optional[list[str]] = None,
        target_name:   Optional[str]       = None,
        cov_type:      Optional[str]       = None,
        alpha:         float               = 0.05,
    ) -> 'Model':
        pass

    def predict(
            self,
            X:              np.ndarray,
            alpha:          float = 0.05,
            return_table:   bool  = False,
    ) -> Union[np.ndarray, dict]:
        
        self._model_is_fitted()
        return _predict(self, X, alpha, return_table)

    def robust_se(self, type: str = "HC3") -> dict:
        self._model_is_fitted()
        return _robust_se(self, type, False)

    def variance_inflation_factor(self) -> dict:
        self._model_is_fitted()
        return _variance_inflation_factor(self)
    
    def inference_table(self) -> dict:
        self._model_is_fitted()
        return _inference_table(self)



@dataclass
class LinearRegression(Model):

    @property
    def model_type(self) -> str:
        return "ols"

    xtx_inv:            Optional[np.ndarray] = field(default=None, repr=False)
    rss:                Optional[float] = None
    tss:                Optional[float] = None
    ess:                Optional[float] = None
    mse:                Optional[float] = None
    rmse:               Optional[float] = None
    f_statistic:        Optional[float] = None
    r_squared:          Optional[float] = None
    r_squared_adjusted: Optional[float] = None
    t_stat_coefficient: Optional[np.ndarray] = field(default=None)

    def fit(
        self,
        X:              np.ndarray,
        y:              np.ndarray,
        feature_names:  Optional[list[str]] = None,
        target_name:    Optional[str] = None,
        cov_type:       Optional[str] = None,
        alpha:          float = 0.05,
    ) -> 'LinearRegression':
        
        _fit(self, X, y, feature_names, target_name, alpha)
        self._post_fit_processing(cov_type)
        return self



@dataclass
class _BaseClassifier(Model):

    xtWx_inv:                Optional[np.ndarray] = field(default=None, repr=False)
    deviance:                Optional[float] = None
    null_deviance:           Optional[float] = None
    null_log_likelihood:     Optional[float] = None
    pseudo_r_squared:        Optional[float] = None
    lr_statistic:            Optional[float] = None
    z_stat_coefficient:      Optional[np.ndarray] = field(default=None, repr=False)
    probabilities:           Optional[np.ndarray] = field(default=None, repr=False)
    classification_accuracy: Optional[float] = None



@dataclass
class LogisticRegression(_BaseClassifier):

    @property
    def model_type(self) -> str:
        return "mle"

    def fit(
        self,
        X:              np.ndarray,
        y:              np.ndarray,
        feature_names:  Optional[list[str]] = None,
        target_name:    Optional[str] = None,
        cov_type:       Optional[str] = None,
        alpha:          float = 0.05,
        max_iter:       int = 100,
        tol:            float = 1e-8,
    ) -> 'LogisticRegression':
        
        _fit(self, X, y, feature_names, target_name, alpha, max_iter, tol)
        self._post_fit_processing(cov_type)
        return self



@dataclass
class MultinomialLogisticRegression(_BaseClassifier):
    
    @property
    def model_type(self) -> str:
        return "multinomial"

    n_classes:      Optional[int] = None
    n_features:     Optional[int] = None
    y_classes:      Optional[np.ndarray] = field(default=None, repr=False)
    y_encoded:      Optional[np.ndarray] = field(default=None, repr=False)

    # TODO - Improve efficiency of the fit function to reduce runtime.

    def fit(
        self,
        X:              np.ndarray,
        y:              np.ndarray,
        feature_names:  Optional[list[str]] = None,
        target_name:    Optional[str] = None,
        cov_type:       Optional[str] = None,
        alpha:          float = 0.05,
        max_iter:       int = 100,
        tol:            float = 1e-8,
    ) -> 'MultinomialLogisticRegression':
        
        _fit(self, X, y, feature_names, target_name, alpha, max_iter, tol)
        self._post_fit_processing(cov_type)
        return self
    


# TODO - Complete this. Model does not converge.
class OrdinalLogisticRegression(MultinomialLogisticRegression):

    @property
    def model_type(self) -> str:
        return "ordinal"

    theta_cutpoints:    Optional[np.ndarray] = field(default=None, repr=False)
    alpha_cutpoints:    Optional[np.ndarray] = field(default=None, repr=False)

    def fit(
        self,
        X:              np.ndarray,
        y:              np.ndarray,
        feature_names:  Optional[list[str]] = None,
        target_name:    Optional[str] = None,
        cov_type:       Optional[str] = None,
        alpha:          float = 0.05,
        max_iter:       int = 100,
        tol:            float = 1e-8,
    ) -> 'OrdinalLogisticRegression':
        
        _fit(self, X, y, feature_names, target_name, alpha, max_iter, tol)
        self._post_fit_processing(cov_type)
        return self
