# regression-inference

![PyPI version](https://img.shields.io/pypi/v/regression-inference)
![License](https://img.shields.io/github/license/axtaylor/python-ordinary_least_squares?color)

[https://pypi.org/project/regression-inference/](https://pypi.org/project/regression-inference/)

```
pip install regression-inference
```

Python packaged designed for inference workflows using MLE and OLS.


### Usage


Import all utilities:

```python
from regression_inference import *
```

Import select utilities:

```python
from regression_inference import LinearRegression, LogisticRegression, summary
```

### Documentation

See the provided notebooks for example workflows.

```
/tests/notebooks/linear_regression_example.ipynb

/tests/notebooks/logit_regression_example.ipynb
```

### Output Example

Stacked outputs using summary

```py
print(summary(model, robust_model))
```

```
==================================================
OLS Regression Results
--------------------------------------------------
Dependent:                     educ    robust educ
--------------------------------------------------
 
const                     7.3256***      7.3256***
                           (0.3684)       (0.4345)
 
paeduc                    0.2144***      0.2144***
                           (0.0241)       (0.0236)
 
maeduc                    0.2569***      0.2569***
                           (0.0271)       (0.0294)
 
age                       0.0241***      0.0241***
                           (0.0043)       (0.0042)

--------------------------------------------------
R-squared                     0.276          0.276
Adjusted R-squared            0.274          0.274
F Statistic                 177.548        177.548
Observations               1402.000       1402.000
Log Likelihood            -3359.107      -3359.107
AIC                        6726.213       6726.213
BIC                        6747.196       6747.196
TSS                       13663.270      13663.270
RSS                        9893.727       9893.727
ESS                        3769.543       3769.543
MSE                           7.077          7.077
==================================================
*p<0.1; **p<0.05; ***p<0.01
```

### Logistic Regression Summary

```
===================================
Logistic Regression Results
-----------------------------------
Dependent:                    GRADE
-----------------------------------
 
const                    -13.0213**
                           (5.1976)
 
GPA                        2.8261**
                           (1.2675)
 
TUCE                         0.0952
                           (0.1179)
 
PSI                        2.3787**
                           (0.9644)

-----------------------------------
Pseudo R-squared              0.374
LR Statistic                 15.404
Observations                 32.000
Log Likelihood              -12.890
Deviance                     25.779
Null Deviance                41.183
AIC                          33.779
BIC                          39.642
===================================
*p<0.1; **p<0.05; ***p<0.01
```

### Coefficient Inference Table

Generate an inference table on fitted model objects. 

The inference table can be converted to a `pd.DataFrame` object.
```py
pd.DataFrame(model.inference_table())
```

```
[Out]: [{'feature': 'const',
         'coefficient': np.float64(7.3256),
         'std_error': np.float64(0.3684),
         't_statistic': np.float64(19.887),
         'P>|t|': '0.000',
         'ci_low_0.05': np.float64(6.603),
         'ci_high_0.05': np.float64(8.048)},
        {'feature': 'paeduc',
         'coefficient': np.float64(0.2144),
         'std_error': np.float64(0.0241),
         't_statistic': np.float64(8.8796),
         'P>|t|': '0.000',
         'ci_low_0.05': np.float64(0.167),
         'ci_high_0.05': np.float64(0.262)},
        {'feature': 'maeduc',
         'coefficient': np.float64(0.2569),
         'std_error': np.float64(0.0271),
         't_statistic': np.float64(9.4725),
         'P>|t|': '0.000',
         'ci_low_0.05': np.float64(0.204),
         'ci_high_0.05': np.float64(0.31)},
        {'feature': 'age',
         'coefficient': np.float64(0.0241),
         'std_error': np.float64(0.0043),
         't_statistic': np.float64(5.5789),
         'P>|t|': '0.000',
         'ci_low_0.05': np.float64(0.016),
         'ci_high_0.05': np.float64(0.033)}]
```

![](./static/3.png)


### Predictions

Extract the order of feature names using `feature_names[:1]`
```
model.feature_names[1:]
```
```
[Out]: Index(['paeduc', 'maeduc', 'age'], dtype='object')
```

Predict in the order of the feature names.
```
model.predict(np.array([[0, 0, 0], ]))
```
```
[Out]: array([7.32564767])
```

### Advanced Predictions

Use iterations to make predictions over a discrete range of values

Use `return_table = True` to generate a dictionary of prediction statistics
instead of an array of values.

```py
prediction_set = [
    (np.array([[i, X['maeduc'].mean(), X['age'].mean()],]))
    for i in range(int(X['paeduc'].min()), int(X['paeduc'].max())+1)
    ] 
predictions = pd.concat([pd.DataFrame(model.predict(i, return_table=True)) for i in prediction_set], ignore_index=True)
predictions
```

![](./static/1.png)

**Predictions on a Logistic Regression Model**

```py
prediction_set = [
    np.array([[2.66, 20.0, 0.0]]),
    np.array([[2.89, 22.0, 0.0]]),
    np.array([[3.28, 24.0, 0.0]]),
    np.array([[2.92, 12.0, 0.0]]),
]
predictions = pd.concat([pd.DataFrame(model.predict(test_set, return_table=True)) for test_set in prediction_set], ignore_index=True)
predictions
```

![](./static/2.png)


### Variance Inflation Factor

Variance Inflation Factor can be generated for the model's features.

```py
model.variance_inflation_factor()
```

Dictionary output can be converted into a `pd.DataFrame` object


```
{'feature': Index(['paeduc', 'maeduc', 'age'], dtype='object'),
 'VIF': array([2.0233, 2.0285, 1.0971])}
```
