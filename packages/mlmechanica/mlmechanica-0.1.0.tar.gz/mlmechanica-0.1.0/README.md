# MLMechanica

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Status](https://img.shields.io/badge/status-active-success)]()

**Machine Learning, Unveiled.**

`mlmechanica` is a custom Machine Learning library built from scratch in
Python. Unlike traditional libraries that treat models as "black boxes,"
MLMechanica is designed to be a **"Glass Box"**---offering complete
transparency into the mathematical operations, internal states, and
iterative steps of every algorithm.

It is strictly educational, optimized for clarity and understanding
rather than production speed.

------------------------------------------------------------------------

## 🚀 Key Features

-   **Transparency First**: Enable the `calculation=True` flag to see
    every matrix multiplication, gradient update, and intermediate
    derivation logged to your console in real-time.
-   **Pure Python & NumPy**: Implementations rely solely on NumPy for
    linear algebra, avoiding high-level abstractions to show exactly how
    the math works.
-   **Self-Documenting Models**: Every class includes a
    `model_analysis()` method that returns the rigorous mathematical
    derivation and theory behind that specific algorithm.
-   **Instant Demos**: Built-in static `demo()` methods allow you to run
    smoke tests and visualize model performance instantly without
    writing setup code.

------------------------------------------------------------------------

## 📦 Installation

### From Source

You can clone the repository directly from GitHub:

``` bash
git clone https://github.com/Sarbik-Mal/mlmechanica.git
cd mlmechanica
pip install .
```

(Note: PyPI installation coming soon via `pip install mlmechanica`)

------------------------------------------------------------------------

## ⚡ Quick Start

### 1. Run a built-in Demo

Want to see Lasso Regression in action immediately? Every model comes
with a static demo that generates synthetic data, trains the model, and
evaluates it.

``` python
from mlmechanica.regression.linear import LassoRegression


LassoRegression.demo()
```

### 2. Custom Usage with "Calculation Mode"

See the internal math (Gradient Descent, Matrix Inversion, etc.) by
setting `calculation=True`.

``` python
import numpy as np
from mlmechanica.regression.linear import MultipleLinearRegression

X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
y = np.array([2, 3, 4, 5])

model = MultipleLinearRegression(calculation=True)

model.fit(X, y)

pred = model.predict(np.array([[5, 6]]))
print(f"Prediction: {pred}")
```

------------------------------------------------------------------------

## 📚 Supported Models

Currently, the library focuses on linear regression techniques:

| Module | Class | Description |
| :--- | :--- | :--- |
| **Simple Linear** | `SimpleLinearRegression` | Univariate regression using closed-form OLS derivation. |
| **Multiple Linear** | `MultipleLinearRegression` | Multivariate regression using the Normal Equation (Vectorized). |
| **Lasso** | `LassoRegression` | L1 Regularization using Coordinate Descent and Soft Thresholding. |
| **Ridge** | `RidgeRegression` | L2 Regularization offering multiple solvers: `lsqr`, `svd`, `cholesky`, and `mbsag` (Stochastic Avg Gradient). |

## 🧠 Model Analysis

Retrieve the mathematical derivation directly from any model:

``` python
from mlmechanica.regression.linear import SimpleLinearRegression

model = SimpleLinearRegression()

print(model.model_analysis('derivation'))
```

------------------------------------------------------------------------

## 🤝 Contributing

Contributions are welcome! This is an educational project, so clarity
and readability are prioritized.

1.  Fork the Project\
2.  Create a Feature Branch (`git checkout -b feature/NewAlgorithm`)\
3.  Commit Changes (`git commit -m 'Add DecisionTree implementation'`)\
4.  Push to Branch (`git push origin feature/NewAlgorithm`)\
5.  Open a Pull Request

------------------------------------------------------------------------

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
