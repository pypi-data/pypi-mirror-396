import numpy as np
from scipy.sparse.linalg import aslinearoperator
import time
import textwrap
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s', force=True)
logger = logging.getLogger(__name__)

class RidgeRegression:
    """
    RidgeRegression Class
    =====================
    A custom implementation of Ridge Regression for educational purposes. This class provides an in-depth understanding of various solvers used to compute Ridge Regression,
    with options to view internal calculations, detailed theoretical and mathematical explanations, and animations to visualize the learning process.
    Ridge Regression applies L2 regularization to linear regression, which helps prevent overfitting by penalizing large coefficients.
    This implementation provides flexibility in parameter tuning and optimization strategies.

    Parameters:
    ----------
    learning_rate : float, optional (default=0.01)
        Learning rate for gradient descent-based optimization. Must be a positive number.
        Smaller values ensure stable convergence, while larger values speed up training but
        may overshoot the minimum.

    max_iter : int or None, optional (default=None)
        The maximum number of iterations allowed for optimization. If None, the optimization
        continues until convergence or early stopping criteria are met.

    batch_size : int, optional (default=16)
        Size of the mini-batches for stochastic gradient descent. Determines how many samples
        are used per optimization step. Must be a positive integer.

    tol : float, optional (default=1e-6)
        The tolerance for optimization convergence. If the change in loss between iterations
        is smaller than this value, optimization stops. Must be a positive number.

    patience : int, optional (default=10)
        Number of consecutive iterations without improvement before early stopping is triggered.
        Must be a non-negative integer.

    alpha : float, optional (default=0.1)
        The regularization strength. Higher values increase regularization, reducing the magnitude
        of coefficients. Must be a non-negative number.

    solver : str, optional (default='auto')
        Optimization solver to use. Options are:
        - 'lsqr': Least Squares solver.
        - 'svd': Singular Value Decomposition.
        - 'cholesky': Cholesky Decomposition.
        - 'mbsag': Mini-Batch Stochastic Average Gradient.
        - 'auto': Automatically selects the appropriate solver based on the problem.

    random_state : int or None, optional (default=None)
        Seed for random number generation to ensure reproducibility. If None, randomness is not seeded.

    calculation : bool, optional (default=False)
        If True, enables additional calculations or analysis during training.

    fit_intercept : bool, optional (default=True)
        Whether to fit an intercept (bias) term. If False, assumes data is already centered.

    verbose : bool, optional (default=False)
        If True, prints detailed information about the optimization process.

    early_stopping : bool, optional (default=False)
        If True, enables early stopping based on `patience` and `tol` criteria.

    Attributes:
    ----------
    weights : numpy.ndarray or None
        Coefficients (weights) of the regression model. Initialized to None.

    bias : float or None
        Intercept (bias) term of the regression model. Initialized to 0 if `fit_intercept=True`,
        otherwise None.

    history : list
        History of loss values during optimization. Useful for analyzing convergence.

    flag : any
        A placeholder attribute for custom flags or state management during training.

    coef_ : numpy.ndarray or None
        Alias for `weights`. Coefficients of the regression model.

    intercept_ : float or None
        Alias for `bias`. Intercept term of the regression model.

    allowed_methods : list of str
        List of allowed methods for this class:
        - 'fit': Fits the model to the data.
        - 'predict': Predicts target values.
        - 'store_output': Stores model outputs (e.g., weights, loss history).
        - 'model_analysis': Analyzes model performance.
        - 'animate': Visualizes the optimization process.

    Raises:
    ----------
    ValueError:
        - If `learning_rate` is not a positive number.
        - If `max_iter` is not an integer or None.
        - If `batch_size` is not a positive integer.
        - If `tol` is not a positive number.
        - If `patience` is not a non-negative integer.
        - If `alpha` is not a non-negative number.
        - If `solver` is not one of ['lsqr', 'svd', 'cholesky', 'mbsag', 'auto'].
        - If `random_state` is not an integer or None.
        - If `calculation`, `fit_intercept`, `verbose`, or `early_stopping` are not boolean values.

    Methods
    -------
    fit(X, y)
        Fits the Ridge Regression model using the specified solver.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The input data matrix.

        y : array-like, shape (n_samples,)
            The target values.

        Workflow
        --------
        1. Selects the solver based on the `solver` parameter.
        2. Calls the respective solver method (__lsqr_solver, __svd_solver, etc.).
        3. Updates `weights` and `bias` attributes based on the results.
        4. Tracks loss and performance in `history` if `verbose=True`.

        Notes
        -----
        - If `calculation=True`, outputs detailed step-by-step computations.
        - Automatically handles scaling and intercept adjustment based on `fit_intercept`.

    predict(X)
        Predicts target values using the learned weights and bias.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The input data matrix.

        Returns
        -------
        y_pred : array-like, shape (n_samples,)
            Predicted values.

        Workflow
        --------
        y_pred = X @ weights + bias

    model_analysis(doc_name)
        Provides a theoretical and mathematical explanation of all solvers and methods.

        Parameters:
        -----------
        doc_name : str
            A string representing the name of the method or explanation to be returned.

        Returns:
        --------
        method or explanation (varies based on `doc_name`):
            Depending on the `doc_name` provided, if the `doc_name` matches, the corresponding method or explanation is returned.

        Raises:
        -------
        ValueError:
            If the `doc_name` is `None` or does not match any of the predefined options,
            a `ValueError` is raised with an appropriate error message.
    
    demo()
        Provides a demonstration of the RidgeRegression model using synthetic data.

    Restricted Methods:
    ===================
    __lsqr_solver(X, y)
        Fits the Ridge model using the Least Squares (LSQR) method.

        Workflow
        --------
        1. Calls the `__lsqr` method to solve Ax = b, where:
            A = (XᵀX +  alpha I), b = Xᵀy
        2. Computes `weights` and updates `bias` if `fit_intercept=True`.

        Notes
        -----
        LSQR solves large-scale sparse linear systems iteratively, ensuring numerical stability.

    __lsqr(A, b, damp=0.0, x0=None)
        Computes the LSQR solution for the system Ax = b.

        Returns
        -------
        weights : array-like
            Optimized weight vector.

        Workflow
        --------
        1. Performs iterative refinement to solve the system.
        2. Handles convergence based on `tol`.

    __sym_ortho(a, b)
        Performs Symmetric Orthogonalization, ensuring numerical stability during LSQR.

    __svd_solver(X, y)
        Fits the Ridge model using Singular Value Decomposition (SVD).

        Workflow
        --------
        1. Decomposes the matrix X as U, S, and Vᵀ.
        2. Computes weights using:
            weights = V @ diag(S / (S² +  alpha )) @ Uᵀy

        Notes
        -----
        SVD is robust for ill-conditioned matrices.

    __svd(a)
        Computes the SVD of a matrix A.

        Returns
        -------
        U : array-like
            Left singular vectors.
        S : array-like
            Singular values.
        Vᵀ : array-like
            Right singular vectors.

    __mbsag_solver(X, y)
        Fits the Ridge model using Mini-Batch Stochastic Average Gradient (MBSAG).

        Workflow
        --------
        1. Splits the data into mini-batches of size `batch_size`.
        2. Updates weights and bias iteratively:
            weights -= learning_rate * gradients
        3. Tracks loss and R² if `verbose=True`.

    __compute_r2_score(y_true, y_pred)
        Computes the R² score to measure model performance.

        Returns
        -------
        r2 : float
            The R² score.

        Formula
        -------
        R² = 1 - (Σ(y_true - y_pred)² / Σ(y_true - mean(y_true))²)

    __compute_gradients(X, y, y_pred)
        Computes gradients for the weights and bias.

        Returns
        -------
        gradients : tuple
            Gradients for weights and bias.

        Formula
        -------
        Gradient = -2Xᵀ(y - Xw - b) + 2 alpha w

    __compute_loss(X, y)
        Computes the Ridge Regression loss.

        Returns
        -------
        loss : float
            Computed loss.

        Formula
        -------
        Loss = ||y - Xw - b||² +  alpha ||w||²

    __cholesky_solver(X, y)
        Fits the Ridge model using Cholesky decomposition.

        Workflow
        --------
        1. Solves Ax = b using Cholesky decomposition, where:
            A = XᵀX +  alpha I, b = Xᵀy
    
    Notes
    -----
    This implementation focuses on educational purposes, emphasizing the intuition and theory behind Ridge Regression.

    Example:
        >>> from mlmechanica.regression.linear import RidgeRegression
        >>> model = RidgeRegression(solver='mbsag', verbose=True, early_stopping=True, calculation=True)
    """

    def __init__(self, learning_rate=0.01, max_iter=None, batch_size=16, tol=1e-6, patience=100, alpha=0.1, solver='auto',
                 random_state=None, calculation=False, fit_intercept=True, verbose=False, early_stopping=False):
        if not isinstance(learning_rate, (int, float)) or learning_rate <= 0:
            raise ValueError("learning_rate must be a positive number.")

        if max_iter is not None and not isinstance(max_iter, int):
            raise ValueError("max_iter must be an integer or None.")

        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError("batch_size must be a positive integer.")

        if not isinstance(tol, (int, float)) or tol <= 0:
            raise ValueError("tol must be a positive number.")

        if not isinstance(patience, int) or patience < 0:
            raise ValueError("patience must be a non-negative integer.")

        if not isinstance(alpha, (int, float)) or alpha < 0:
            raise ValueError("alpha must be a non-negative number.")

        if solver not in ['lsqr', 'svd', 'cholesky', 'mbsag', 'auto']:
            raise ValueError("solver must be one of ['lsqr', 'svd', 'cholesky', 'mbsag', 'auto'].")

        if random_state is not None and not isinstance(random_state, int):
            raise ValueError("random_state must be an integer or None.")

        if not isinstance(calculation, bool):
            raise ValueError("calculation must be a boolean value.")

        if not isinstance(fit_intercept, bool):
            raise ValueError("fit_intercept must be a boolean value.")

        if not isinstance(verbose, bool):
            raise ValueError("verbose must be a boolean value.")

        if not isinstance(early_stopping, bool):
            raise ValueError("early_stopping must be a boolean value.")

        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.batch_size = batch_size
        self.tol = tol
        self.patience = patience
        self.alpha = alpha
        self.solver = solver
        self.random_state = random_state
        self.calculation = calculation
        self.fit_intercept = fit_intercept
        self.verbose = verbose
        self.early_stopping = early_stopping
        self.weights = None
        self.bias = 0 if self.fit_intercept else None
        self.history = []
        self.flag = None
        self.coef_ = self.weights
        self.intercept_ = self.bias
        self.allowed_methods = ['fit', 'predict', 'store_output', 'model_analysis','animate']


    def fit(self,X,y):
        """
        This method fits a Ridge Regression model to the provided data `X` (features) and `y` (target labels).

        The `fit` method performs the following tasks:
        1. Data Preparation: Converts the input data `X` and `y` into numpy arrays if they are not already. This ensures that the data can be processed in a consistent manner.
        2. Input Validation:
            - Verifies that the number of rows in `X` matches the length of `y`. If they don't match, a `ValueError` is raised.
            - Checks that the specified solver is one of the supported solvers (`'lsqr'`, `'svd'`, `'cholesky'`, `'mbsag'`, or `'auto'`). If the solver is invalid, it raises a `ValueError`.
        3. Solver Selection: Based on the value of `self.solver` and the characteristics of the data (`X.shape[0]` and `X.shape[1]`), the appropriate solver is selected. The solvers available are:
            - 'lsqr': Least squares solver used for larger datasets.
            - 'mbsag': Mini-batch Stochastic Average Gradient solver, generally used for datasets with many features or smaller datasets.
            - 'svd': Singular Value Decomposition solver, a more computationally expensive method.
            - 'cholesky': Cholesky decomposition solver, used when the matrix is well-conditioned.
            - 'auto': Automatically chooses between `'lsqr'` and `'mbsag'` based on the size of the dataset.
        4. Calling the Appropriate Solver:
            - If the solver is `'lsqr'` or if the solver is set to `'auto'` and the number of samples (`X.shape[0]`) is greater than the number of features (`X.shape[1]`), the `__lsqr_solver` method is called.
            - If the solver is `'mbsag'` or if the solver is set to `'auto'` and the number of samples is less than or equal to the number of features, the `__mbsag_solver` method is invoked.
            - For `'svd'`, the `__svd_solver` method is used, and similarly for `'cholesky'`, the `__cholesky_solver` method is invoked.
        5. Error Handling: If any exception occurs during the execution of the `fit` method, the exception is caught and printed as an error message. The exception is then raised again to propagate the error.

        Parameters:
        - X (array-like or dataframe): The feature matrix (n_samples, n_features).
        - y (array-like or dataframe): The target vector (n_samples,).

        Returns:
        - self: The current instance of the class, which now contains the fitted model.

        Raises:
        - ValueError: If the number of samples in `X` doesn't match the length of `y`, or if an unsupported solver is selected.
        - ValueError: If `verbose` or `early_stopping` are enabled with unsupported solvers.
        - Exception: Any unexpected errors occurring during the fitting process.

        Example:
            >>> import numpy as np
            >>> from mlmechanica.regression.linear import RidgeRegression
            >>> X = np.array([1, 2, 3, 4, 5])
            >>> y = np.array([2, 4, 5, 4, 5])
            >>> model = RidgeRegression()
            >>> model.fit(X, y)
        """
        X, y = np.asarray(X), np.asarray(y)

        if (self.verbose or self.early_stopping) and not (self.solver == 'mbsag' or (self.solver == 'auto' and X.shape[0] <= X.shape[1])):
            raise ValueError("verbose and early_stopping can only be enabled when solver is 'mbsag' or solver is 'auto' and the number of samples (X.shape[0]) is less than or equal to the number of features (X.shape[1]).")

        if X.shape[0] != y.shape[0]:
            raise ValueError("The number of rows in X must match the length of y.")

        if self.solver not in ['lsqr', 'svd', 'cholesky', 'mbsag', 'auto']:
            raise ValueError(f"Solver '{self.solver}' is not supported. Use 'lsqr', 'svd', 'cholesky', 'mbsag', or 'auto'.")

        if self.solver == 'lsqr' or (self.solver == 'auto' and X.shape[0] > X.shape[1]):
            super().__getattribute__("_RidgeRegression__lsqr_solver")(X, y)
            self.flag = 'lsqr'
        elif self.solver == 'mbsag' or (self.solver == 'auto' and X.shape[0] <= X.shape[1]):
            super().__getattribute__("_RidgeRegression__mbsag_solver")(X, y)
            self.flag = 'mbsag'
        elif self.solver == 'svd':
            super().__getattribute__("_RidgeRegression__svd_solver")(X, y)
            self.flag = 'svd'
        elif self.solver == 'cholesky':
            super().__getattribute__("_RidgeRegression__cholesky_solver")(X, y)
            self.flag = 'cholesky'
        else:
            raise ValueError(f"Unknown solver '{self.solver}'.")

        return self


    def predict(self, X):
        """
        This method makes predictions using the fitted Ridge Regression model. It calculates the predicted values
        for the input data `X` (features) based on the learned weights and bias.

        The `predict` method performs the following tasks:
        1. Data Conversion: Converts the input data `X` into a numpy array to ensure compatibility with the model's operations.
        2. Model Check:
            - Verifies if the model has been fitted by checking whether `self.weights` is not `None`. If the model is not fitted, it raises a `ValueError` prompting the user to call the `fit` method first.
        3. Feature Validation:
            - Checks whether the number of features in the input data `X` matches the number of features the model was trained on (i.e., the number of elements in `self.weights`). If the number of features doesn't match, a `ValueError` is raised.
        4. Prediction Calculation:
            - If `self.fit_intercept` is `True`, the method computes the predicted values by performing a dot product of `X` and `self.weights`, then adding the bias term (`self.bias`).
            - If `self.fit_intercept` is `False`, it simply computes the dot product between `X` and `self.weights` without adding a bias term.
        5. Error Handling: If any exception occurs during the execution of the `predict` method, the exception is caught and a `RuntimeError` is raised with a relevant error message.

        Parameters:
        - X (array-like or dataframe): The feature matrix (n_samples, n_features) for which predictions are to be made.

        Returns:
        - (numpy array): The predicted values for the input data `X`, which can be a vector of shape (n_samples,).

        Raises:
        - ValueError: If the model has not been fitted or if the number of features in `X` does not match the number of features used during training.
        - RuntimeError: Any unexpected errors occurring during the prediction process.

        Example:
            >>> X_new = np.array([6, 7])
            >>> predictions = model.predict(X_new)
            >>> print(predictions)
        """
        X = np.asarray(X)
        if self.weights is None:
            raise ValueError("Model is not fitted yet. Call 'fit' before predicting.")
        if X.shape[1] != self.weights.shape[0]:
            raise ValueError("The number of features didn't matched with the fitted X.")

        if self.fit_intercept:
            if self.calculation:
                logger.info(f"\nPrediction = X @ weights + bias:\n{X.dot(self.weights) + self.bias}\n")
            return X.dot(self.weights) + self.bias
        else:
            if self.calculation:
                logger.info(f"\nPrediction = X @ weights:\n{X.dot(self.weights)}\n")
            return X.dot(self.weights)


    def __lsqr_solver(self, X, y):
        self.count_lsqr = {
            "lsqr":True,
            "lsqr_condition_1":True,
            "lsqr_condition_2":True,
            "lsqr_condition_3":True,
            "lsqr_condition_4":True,
            "lsqr_condition_5":True,
            "lsqr_condition_6":True,
            "lsqr_condition_7":True,
            "lsqr_condition_8":True,
            "sym_ortho":True,
            "sym_ortho_condition_1":True,
            "sym_ortho_condition_2":True,
            "sym_ortho_condition_3":True,
            "sym_ortho_condition_4":True,
        }
        if self.calculation:
            logger.info(f"""
\n<--------------------------------------Ftting using LSQR method-------------------------------------->\n
{'='*200}

The purpose of the `lsqr_solver` method is to compute the weights (coefficients) and biases for a regression model using the LSQR algorithm with optional regularization.

1. Why it is used:
- It solves the linear equation (X^T X + alpha I)w = X^T y, where alpha is the regularization parameter.
- The method determines the optimal weights (w) by minimizing the regularized least squares loss.

2. Importance in machine learning models:
- Incorporates L2 regularization (via alpha) to handle overfitting and improve generalization.
- Supports fitting models with or without an intercept, adjusting the input data accordingly.

3. Role in the regression workflow:
- Preprocesses the data by centering it (if `fit_intercept=True`) to ensure proper bias computation.
- Regularizes the feature matrix X to stabilize the inversion of X^T X, particularly for ill-conditioned or high-dimensional data.
- Computes and stores the weights and bias for use during predictions.

4. Key considerations:
- Ensures that the dimensions of X and y are compatible for matrix operations.
- Handles multi-output regression by iteratively solving for each output column.

{'='*200}
""")

        X, y = np.asarray(X), np.asarray(y)

        if y.ndim == 1:
            y = np.atleast_2d(y).T
        elif y.ndim > 2:
            raise ValueError("y must be 1D or 2D.")

        if y.shape[0] != X.shape[0]:
            if y.T.shape[0] == X.shape[0]:
                y = y.T
            else:
                raise ValueError(f"Dimension mismatch: X has {X.shape[0]} rows but y has {y.shape[0]} rows.")

        if not hasattr(self, 'fit_intercept') or not hasattr(self, 'alpha'):
            raise AttributeError("Attributes 'fit_intercept' or 'alpha' are not set.")

        if self.calculation:
            logger.info(f"Given X:\n{X}\n")
            logger.info(f"Given y:\n{y}\n")

        if self.fit_intercept:
            X_mean = np.mean(X, axis=0, keepdims=True)
            y_mean = np.mean(y, axis=0, keepdims=True)
            X = X - X_mean
            y = y - y_mean
            if self.calculation:
                logger.info("Applying Mean Centering (AS fit_intercept = True)")
                logger.info(f"X_mean: \n{X_mean}\n")
                logger.info(f"y_mean: \n{y_mean}\n")
        else:
            X_mean = np.zeros((1, X.shape[1]))
            y_mean = np.zeros((1, y.shape[1]))
            if self.calculation:
                logger.info("Not applying Mean Centering (AS fit_intercept = False)")
                logger.info(f"X_mean: \n{X_mean}\n")
                logger.info(f"y_mean: \n{y_mean}\n")

        m, n = X.shape
        I = np.eye(n)
        if self.calculation:
            logger.info(f"Taking Indentity matrix with shape ({n}, {n})")
        XTX = X.T @ X
        XTy = X.T @ y
        regularized_XTX = XTX + self.alpha * I
        if self.calculation:
            logger.info(f"XTX = Transpose of X . X: \n{XTX}\n")
            logger.info(f"XTy = Transpose of X . y: \n{XTy}\n")
            logger.info(f"regularized_XTX = XTX + alpha * Identity matrix: \n{regularized_XTX}\n")

        weights = []
        for i in range(y.shape[1]):
            if self.calculation:
                logger.info(f"\nSolving for weights of output column {i}:")
                logger.info(f"{'=' * 50}\n")
            result = self.__lsqr(regularized_XTX, XTy[:, i])
            coef = result
            weights.append(coef)
            if self.calculation:
                logger.info(f"Applying lsqr method with regularized_XTX and all values of XTy till {i}th")
                logger.info(f"Weights for output column {i}: \n{coef}\n")

        self.weights = np.array(weights).T
        self.bias = y_mean - (X_mean @ self.weights) if self.fit_intercept else np.zeros((1, y.shape[1]))
        if self.calculation:
            logger.info(f"Final Weights => Transpose of Weights: \n{self.weights}\n")
            if self.fit_intercept:
                logger.info(f"Final Bias => y_mean - (X_mean @ self.weights): \n{self.bias}\n")
            else:
                logger.info(f"Final Bias => Zero matrix with shape {1}, {y.shape[1]}\n")


    def __lsqr(self, A, b, damp=0.0, x0=None):
        if self.calculation:
            logger.info("\n<--------------------------------------Computing LSQR-------------------------------------->\n")
            if self.count_lsqr['lsqr']:
                logger.info(f"""
{'='*200}

The purpose of the `lsqr` method is to solve linear equations of the form Ax = b using the LSQR algorithm, which is an iterative method for solving sparse or ill-conditioned systems.

1. Why it is used:
- It efficiently computes solutions to large, sparse, or ill-conditioned linear systems by minimizing the squared residuals (||Ax - b||^2).
- It incorporates damping (regularization) to handle stability and convergence issues in ill-posed problems.

2. Importance in iterative solvers:
- Avoids directly inverting the matrix A, which can be computationally expensive or numerically unstable for large systems.
- Iteratively refines the solution by updating residuals and directions at each step, ensuring convergence toward the optimal solution.

3. Key functionalities:
- Handles damping (regularization) to stabilize the solution for ill-conditioned systems.
- Uses Givens rotations (computed with Symmetric Orthogonalization Computation) to maintain numerical stability and update residuals efficiently.
- Incorporates an initial guess (x0) if provided, allowing flexibility in starting the iteration process.

4. Role in regression and optimization:
- Essential for solving the regularized normal equations in regression models.
- Provides the backbone for efficient and stable computation of weights (coefficients) during model fitting.

5. Key considerations:
- Ensures compatibility of input dimensions for A and b.
- Dynamically adjusts iteration limits to ensure convergence within computational constraints.

{'='*200}
""")

            logger.info(f"Given A (values of regularized_XTX):\n{A}\n")
            logger.info(f"Given b (values of XTy):\n{b}\n")

        try:
            A = aslinearoperator(A)
        except Exception as e:
            raise ValueError(f"Error converting A to a linear operator: {e}")
        if self.calculation:
            logger.info("Converting A into linear operator using `aslinearoperator`")
            if self.count_lsqr['lsqr']:
                logger.info(f"""
{'='*200}

The purpose of this line is to ensure that the matrix or array A is converted into a linear operator, which can be used efficiently for matrix-vector and matrix-matrix operations in the `scipy.sparse.linalg` context.

1. Why it is used:
- The `aslinearoperator` function is used to convert various types of inputs (such as NumPy arrays, sparse matrices, or other compatible objects) into an object that behaves like a linear operator.
- This allows the linear algebra operations to be handled more efficiently, especially with sparse matrices, and ensures that the subsequent computations can leverage optimized methods for matrix-vector multiplication.

2. What it does:
- It checks if A is already a linear operator, and if not, it converts it into one.
- A linear operator is an object that supports the `matvec` (matrix-vector multiplication) and `rmatvec` (reverse matrix-vector multiplication) methods, which are used in iterative solvers like the LSQR algorithm.

3. Importance in the `lsqr` method:
- This conversion is essential for ensuring that the matrix A can be used efficiently in sparse linear algebra computations, particularly when dealing with large matrices that may be sparse.
- It helps in managing memory efficiently and speeds up the matrix-vector multiplication processes during the iterative solution process.

{'='*200}
""")
                self.count_lsqr['lsqr']=False


        b = np.atleast_1d(b)
        if b.ndim > 1:
            if b.shape[1] == 1:
                b = b.squeeze()
            else:
                raise ValueError(f"Invalid dimensions for b: {b.shape}")

        num_rows, num_cols = A.shape
        if self.max_iter is None:
            iter_lim = 2 * min(num_rows, num_cols)

        if not isinstance(iter_lim, int) or iter_lim <= 0:
            raise ValueError(f"Invalid iteration limit: {iter_lim}")

        iteration = 0
        regularization_norm = 0
        damping_square = damp**2

        residual = b
        norm_b = np.linalg.norm(b)
        if self.calculation:
            logger.info("\nInitializing values\n")
            logger.info(f"damping_square = {damp**2}")
            logger.info(f" residual = {b}")
            logger.info(f"Normalization of b: {norm_b}\n")


        if x0 is None:
            solution = np.zeros(num_cols)
            residual_norm = norm_b.copy()
            if self.calculation:
                logger.info(f"\nSolution: zero matrix of {num_cols} ,{num_cols}")
                logger.info(f"Residual Norm: {residual_norm}\n")
        else:
            solution = np.asarray(x0)
            if solution.shape != (num_cols,):
                raise ValueError(f"Initial guess x0 must have shape ({num_cols},), but got {solution.shape}")
            residual = residual - A.matvec(solution)
            residual_norm = np.linalg.norm(residual)
            if self.calculation:
                logger.info(f"\nSolution: \n{solution}\n")
                logger.info(f"residual = residual - A.matvec(solution): {residual}")
                logger.info(f"residual_norm = Normalization of residual: {residual_norm}\n")

        if residual_norm > 0:
            residual /= residual_norm
            direction = A.rmatvec(residual)
            direction_norm = np.linalg.norm(direction)
            if self.calculation:
                logger.info("\nAs residual_norm > 0\n")
                logger.info(f"residual = residual/residual_norm")
                logger.info(f"direction = A.rmatvec(residual): {direction}")
                logger.info(f"direction_orm = Normalization of direction: {direction_norm}\n")
                if self.count_lsqr['lsqr_condition_1']:
                    logger.info(f"""
{'='*200}

The purpose of this case is to normalize the residual vector and compute the direction for the next iteration in the iterative solver process.

1. Why it is used:
- The residual represents the difference between the current solution and the desired solution.
- Normalizing the residual ensures that it has a unit norm, which improves the numerical stability and efficiency of the iterative process.
- The direction is then calculated by applying the transpose of the matrix A to the residual, which determines the next search direction for minimizing the residual.

2. What it does:
- `residual_norm` is checked to ensure that the residual is not a zero vector.
- The residual is divided by its norm to normalize it. This step ensures that the residual has a unit norm (magnitude of 1), making the subsequent iterations more stable.
- `direction` is computed by applying the reverse matrix-vector multiplication (`rmatvec`) of the matrix A to the normalized residual. This computes the direction for the next step in the iterative process.
- `direction_norm` is the norm of the resulting direction vector. This value is used to scale the direction vector appropriately in the next iteration.

3. Importance in the Iterative Solver:
- Normalizing the residual helps in maintaining numerical stability and prevents issues like divergence in iterative methods.
- The direction is crucial for updating the solution in each iteration of the algorithm, and the `rmatvec` operation ensures the direction is aligned with the desired solution.

{'='*200}
""")
                    self.count_lsqr['lsqr_condition_1']=False

        else:
            direction = solution.copy()
            direction_norm = 0
            if self.calculation:
                logger.info("\nAs residual_norm == 0\n")
                logger.info(f"direction=solution")
                logger.info(f"direction_orm = Normalization of direction: {direction_norm}\n")
                if self.count_lsqr['lsqr_condition_2']:
                    logger.info(f"""
{'='*200}

The purpose of this case is to handle the scenario where the residual has a zero norm, indicating that the current solution is already sufficiently close to the desired result or there is no remaining residual.

1. Why it is used:
- When the residual norm is zero, it implies that the solution has converged, or no further improvement is needed.
- In this case, instead of further computations, the direction is set to the current solution, and no additional direction is needed for the next iteration.

2. What it does:
- `direction` is set to a copy of the current solution, since there is no need to compute a new direction when the residual has been reduced to zero.
- `direction_norm` is set to zero, indicating that no further direction is needed because the solution is already optimal or the residual is zero.

3. Importance in the Iterative Solver:
- This step ensures that the algorithm terminates when the residual becomes sufficiently small (or zero), preventing unnecessary iterations and improving efficiency.
- By setting the direction to the solution, it prevents further updates and allows the algorithm to conclude.

{'='*200}
""")
                    self.count_lsqr['lsqr_condition_2']=False


        if direction_norm > 0:
            direction /= direction_norm
            if self.calculation:
                logger.info("\nAs direction_norm > 0")
                logger.info(f"\ndirection = direction/direction_norm:\n{direction}\n")
                if self.count_lsqr['lsqr_condition_3']:
                    logger.info(f"""
{'='*200}

The purpose of this step is to normalize the direction vector, ensuring it has a unit norm before being used for the next iteration in the iterative solver.

1. Why it is used:
- Normalizing the direction vector ensures that it has a unit length (norm of 1), which improves the stability and convergence of the iterative algorithm.
- This normalization step prevents the direction vector from growing too large or becoming too small, which can destabilize the iterative process.

2. What it does:
- `direction_norm > 0` ensures that the direction vector is not a zero vector, which would indicate that no further movement is needed.
- If the direction norm is positive, the direction vector is divided by its norm to normalize it, making its magnitude equal to 1 while preserving its direction.

3. Importance in the Iterative Solver:
- Normalizing the direction vector ensures that each iteration progresses in a stable manner, with the direction update having a consistent scale.
- It prevents any issues with scaling that could otherwise affect the convergence of the solution.

{'='*200}
""")
                    self.count_lsqr['lsqr_condition_3']=False

        step = direction.copy()
        if self.calculation:
            logger.info("step = direction\n")

        rhobar = direction_norm
        phibar = residual_norm
        arnorm = direction_norm * residual_norm
        if self.calculation:
            logger.info("\nrhobar = direction_norm")
            logger.info("phibar = residual_norm")
            logger.info(f"arnorm = direction_norm * residual_norm: {arnorm}\n")
            if self.count_lsqr['lsqr_condition_3']:
                logger.info(f"""
{'='*200}

The purpose of these calculations is to update the variables that are used in the iterative process of the LSQR solver, which help control the progress of the algorithm.

1. Why it is used:
- `rhobar` and `phibar` represent the norms of the direction and residual vectors, respectively. These values are used in the iterative process to track the progress of the solution.
- `arnorm` is the product of the direction and residual norms. This value represents the current "work" being done by the algorithm to minimize the residual, and it is used in the termination condition and updating the solution.

2. What it does:
- `rhobar` is assigned the value of `direction_norm`, which represents the magnitude of the current direction vector.
- `phibar` is assigned the value of `residual_norm`, which represents the magnitude of the current residual vector.
- `arnorm` is the product of `direction_norm` and `residual_norm`, which quantifies the interaction between the direction and residual, contributing to the stopping criterion and solution update.

3. Importance in the Iterative Solver:
- These variables are essential for tracking the progress of the solver and for controlling how the solution is updated at each step.
- `arnorm` is a key factor in determining whether the algorithm has converged or if additional iterations are needed. If this value becomes sufficiently small, the algorithm terminates.

{'='*200}
""")
                self.count_lsqr['lsqr_condition_3']=False

        if arnorm == 0:
            if self.calculation:
                logger.info(f"as arnorm = 0 returning the solution:{solution}\n")
                if self.count_lsqr['lsqr_condition_4']:
                    logger.info(f"""
{'='*200}

The purpose of this check is to handle the case where the algorithm has converged or no further improvements can be made, and therefore the current solution is returned.

1. Why it is used:
- `arnorm` represents the product of the direction and residual norms. If `arnorm` equals zero, it indicates that either the residual or direction has reached zero, meaning the solution has converged.
- In this case, there's no need for further iterations, as the algorithm has effectively found the solution.

2. What it does:
- If `arnorm` is zero, the algorithm prints a message and then returns the current `solution`, as it has reached a state where no further iterations are required.

3. Importance in the Iterative Solver:
- This is a crucial check for stopping the iterative process when the residual and direction have been minimized sufficiently. Returning the solution when `arnorm` equals zero prevents unnecessary computation and ensures the solver terminates once a solution is found.
- It helps in improving the efficiency and convergence of the algorithm.

{'='*200}
""")
                self.count_lsqr['lsqr_condition_4']=False
            return solution

        while iteration < iter_lim:
            iteration += 1

            try:
                residual = A.matvec(direction) - direction_norm * residual
                residual_norm = np.linalg.norm(residual)
            except Exception as e:
                raise RuntimeError(f"Error during matrix-vector operations at iteration {iteration}: {e}")
            if self.calculation:
                logger.info(f"\nresidual = A.matvec(direction) - direction_norm * residual: {residual}")
                logger.info(f"residual_norm = Normalization of residual: {residual_norm}\n")
                if self.count_lsqr['lsqr_condition_5']:
                    logger.info(f"""
{'='*200}

The purpose of these operations is to update the residual vector and calculate its new norm in the iterative process of the LSQR solver.

1. Why it is used:
- The residual represents the difference between the current solution and the target solution. Updating the residual ensures that the algorithm continues to minimize this difference.
- The updated residual will guide the direction of further iterations, and its norm will indicate how close the solution is to convergence.

2. What it does:
- `residual` is updated by applying the matrix-vector multiplication (`A.matvec(direction)`) to the current `direction` and subtracting a scaled version of the previous `residual`. This operation refines the residual vector based on the direction and helps in guiding the search for the solution.
- `residual_norm` is recalculated by computing the Euclidean norm of the updated `residual`. This value indicates the magnitude of the residual, and it will be used to track the convergence of the solution.

3. Importance in the Iterative Solver:
- Updating the residual is critical to reflect the current state of the solution and refine the search direction in subsequent iterations.
- The `residual_norm` helps in determining the stopping criterion for the algorithm, as the solver should terminate when the residual becomes sufficiently small.

{'='*200}
""")
                    self.count_lsqr['lsqr_condition_5']=False

            if residual_norm > 0:
                residual /= residual_norm
                regularization_norm = np.sqrt(regularization_norm**2 + direction_norm**2 + residual_norm**2 + damping_square)
                direction = A.rmatvec(residual) - residual_norm * direction
                direction_norm = np.linalg.norm(direction)
                if self.calculation:
                    logger.info("\nAs Normalized Residual is positive\n")
                    logger.info(f"regularization_norm = Square root of (regularization_norm^2 + direction_norm^2 + residual_norm^2 + damping_square):{regularization_norm}\n")
                    logger.info(f"direction = A.rmatvec(residual) - residual_norm * direction: {direction}")
                    logger.info(f"direction_norm = Normalization of direction: {direction_norm}\n")
                    if self.count_lsqr['lsqr_condition_6']:
                        logger.info(f"""
{'='*200}

The purpose of these operations is to normalize the residual vector, update the regularization term, and refine the direction vector during the iterative process.

1. Why it is used:
- `residual_norm > 0` ensures that the residual vector is non-zero before performing further calculations. Normalizing the residual and updating the direction ensures the algorithm continues moving toward the optimal solution.
- `regularization_norm` accumulates the magnitude of the direction, residual, and damping terms, which helps in controlling the regularization and convergence of the solver.
- `direction` and `direction_norm` are recalculated to refine the search for the solution in the next iteration.

2. What it does:
- `residual /= residual_norm` normalizes the residual vector so that its norm is 1, ensuring it has consistent scaling during further iterations.
- `regularization_norm` is updated by adding the squared magnitudes of the direction, residual, and damping terms. This helps in controlling the overall regularization in the solver.
- `direction` is updated by applying the matrix-vector multiplication (`A.rmatvec(residual)`) to the normalized residual and subtracting the scaled direction to refine the search direction.
- `direction_norm` is recalculated as the Euclidean norm of the updated `direction`, ensuring it has a consistent magnitude for the next iteration.

3. Importance in the Iterative Solver:
- Normalizing the residual vector and updating the direction ensures the solver moves toward a solution in a stable and efficient manner.
- The `regularization_norm` helps in controlling the regularization, ensuring the algorithm balances between fitting the data and preventing overfitting.
- By refining the direction and its norm, the solver ensures that each iteration makes meaningful progress toward the optimal solution.

{'='*200}
""")
                        self.count_lsqr['lsqr_condition_6']=False

                if direction_norm > 0:
                    direction /= direction_norm
                    if self.calculation:
                        logger.info("direction = direction/direction_norm\n")

            if damp > 0:
                rhobar1 = np.sqrt(rhobar**2 + damping_square)
                cs1 = rhobar / rhobar1
                phibar = cs1 * phibar
                if self.calculation:
                    logger.info(f"\nAs damp > 0")
                    logger.info(f"rhobar1 = Square root of (rhobar^2 + damping_square):{rhobar1}")
                    logger.info(f"cs1 = rhobar / rhobar1:{cs1}")
                    logger.info(f"phibar = cs1 * phibar:{phibar}\n")
                    if self.count_lsqr['lsqr_condition_7']:
                        logger.info(f"""
{'='*200}

The purpose of these operations is to apply damping to the iterative process, adjusting the variables that influence the solution to ensure stability and control.

1. Why it is used:
- The `damp > 0` check ensures that damping is applied only when needed, preventing the update of variables when damping is not required (i.e., when `damp == 0`).
- Damping is used to regulate the magnitude of the solution update and prevent instability or excessive oscillations in the iterative process.

2. What it does:
- `rhobar1` is updated by adding the square of the damping term to `rhobar`. This adjustment incorporates the effect of damping, ensuring the solution remains stable.
- `cs1` is computed as the ratio of `rhobar` to `rhobar1`, effectively scaling the progress of the iteration.
- `phibar` is updated by multiplying it with `cs1`, modifying it in accordance with the damping factor to control the solution's adjustment during the iteration.

3. Importance in the Iterative Solver:
- Damping helps stabilize the iterative process, especially when the residuals or directions are large or oscillatory. It smooths the updates to the solution, ensuring more gradual and stable convergence.
- The updated `rhobar1` and `cs1` values allow for controlled progression of the solution, especially when adjusting for residuals that may otherwise lead to instability.
- Damping is a common technique in iterative solvers to enhance convergence and prevent divergence due to large updates or oscillations in the solution path.

{'='*200}
""")
                        self.count_lsqr['lsqr_condition_7']=False

            else:
                rhobar1 = rhobar
                if self.calculation:
                    logger.info(f"\nAs damp <= 0")
                    logger.info(f"rhobar = rhobar:{rhobar1}\n")

            try:
                if self.calculation:
                    logger.info(f"\nComputing cosine, sine and rho for iteration {iteration+1}\n")
                cosine, sine, rho = self.__sym_ortho(rhobar1, residual_norm)
            except Exception as e:
                raise RuntimeError(f"Error in __sym_ortho at iteration {iteration}: {e}")

            if self.calculation:
                logger.info(f"\nApplying Symmetric Orthogonalization of rhobar1 and residual_norm\n")

            rhobar = -cosine * direction_norm
            phi = cosine * phibar
            phibar = sine * phibar
            t1 = phi / rho
            solution = solution + t1 * step
            step = direction + (-sine * t1 / rho) * step
            if self.calculation:
                logger.info(f"rhobar = -cosine * direction_norm:{rhobar}")
                logger.info(f"phi = cosine * phibar:{phi}")
                logger.info(f"phibar = sine * phibar:{phibar}")
                logger.info(f"t1 = phi / rho:{t1}")
                logger.info(f"solution = solution + t1 * step:{solution}")
                logger.info(f"step = direction + (-sine * t1 / rho) * step:{step}\n")
                if self.count_lsqr['lsqr_condition_8']:
                    logger.info(f"""
{'='*200}

The purpose of these operations is to update the solution and step variables during the iterative process by using the orthogonalization parameters and direction vectors.

1. Why it is used:
- These calculations are part of the iterative process in the LSQR method, where the algorithm updates the solution vector based on the current direction, residuals, and orthogonalization parameters (cosine, sine, etc.).
- The goal is to refine the solution with each iteration by adjusting the solution and step variables, ensuring convergence to the optimal solution.

2. What it does:
- `rhobar` is updated by scaling the `direction_norm` with the `cosine` factor. This adjusts the progress of the solution in the current direction.
- `phi` is updated as the product of `cosine` and `phibar`, refining the current parameter.
- `phibar` is updated by multiplying it with `sine`, accounting for the change in the orthogonalization process.
- `t1` is computed as the ratio of `phi` to `rho`, determining the step size for adjusting the solution.
- `solution` is updated by adding the scaled `step` (multiplied by `t1`), moving the solution toward the optimal value.
- `step` is updated by adjusting the `direction` and further refining it using the `sine` and `t1` factors, ensuring the solution converges properly.

3. Importance in the Iterative Solver:
- These updates are crucial for refining the solution and ensuring that the algorithm moves in the correct direction to converge to the optimal solution.
- The updates to `solution` and `step` ensure that the iterative process progresses in a stable and controlled manner.
- These calculations incorporate the effect of the orthogonalization parameters, ensuring the solver performs the necessary adjustments to the solution in each iteration for improved accuracy and convergence.

{'='*200}
""")
                    self.count_lsqr['lsqr_condition_8']=False

        return solution


    def __sym_ortho(self, a, b):
        try:
            if self.calculation:
                logger.info("\n<--------------------------------------Computing Symmetric Orthogonalization-------------------------------------->\n")
                if self.count_lsqr['sym_ortho']:
                    logger.info(f"""
{'='*200}

The purpose of the Symmetric Orthogonalization Computation is to compute a stable orthogonal transformation, specifically for applying Givens rotations in numerical algorithms.

1. Why it is used:
- It transforms a 2D vector (a, b) into (r, 0) while preserving its magnitude.
- It calculates the cosine (c) and sine (s) of the rotation and the radius (r), which represents the magnitude of the original vector.

2. Importance in the LSQR solver:
- Ensures numerical stability during iterative processes, especially when dealing with ill-conditioned matrices.
- Helps update parameters like residuals, directions, and orthogonality conditions to ensure the solver converges properly.

3. Role in maintaining stability:
- Prevents large numerical errors during computation.
- Provides a foundation for iterative refinement in LSQR, enabling it to make reliable progress toward the solution.

{'='*200}
""")
                    self.count_lsqr['sym_ortho']=False

            if b == 0:
                cosine = np.sign(a) if a != 0 else 1
                sine = 0
                radius = abs(a)
                if self.calculation:
                    logger.info(f"\nAs b == 0")
                    logger.info(f"cosine = sign of a if a != 0 else 1:{cosine}")
                    logger.info("sine = 0\n")
                    logger.info(f"radius = absolute of a:{radius}\n")
                    if self.count_lsqr['sym_ortho_condition_1']:
                        logger.info(f"""
{'='*200}

The purpose of this case is to handle the special case where the second component of the 2D vector (b) is zero, ensuring the stability of the orthogonal transformation.

1. Why it is used:
- If b == 0, the orthogonal transformation simplifies since there is no contribution from the second component (b).
- The cosine and sine values are computed based solely on the first component (a).

2. What it does:
- If a is non-zero, the cosine is set to the sign of a, ensuring the transformation preserves the vector's direction.
- If a is zero, the cosine defaults to 1 as a fallback.
- The sine is set to 0 since b is zero, meaning no rotation along the second axis is needed.
- The radius is calculated as the absolute value of a, representing the magnitude of the vector after the transformation.

3. Importance in the Symmetric Orthogonalization Computation:
- Provides a stable and consistent way to compute the orthogonal transformation when one component of the vector is zero.
- Prevents division by zero or undefined behavior in the orthogonalization process.

{'='*200}
""")
                        self.count_lsqr['sym_ortho_condition_1']=False

            elif a == 0:
                cosine = 0
                sine = np.sign(b)
                radius = abs(b)
                if self.calculation:
                    logger.info(f"\nAs a == 0")
                    logger.info("cosine = 0\n")
                    logger.info(f"sine = sign of b:{sine}")
                    logger.info(f"radius = absolute of b:{radius}\n")
                    if self.count_lsqr['sym_ortho_condition_2']:
                        logger.info(f"""
{'='*200}

The purpose of this case is to handle the special case where the first component of the 2D vector (a) is zero, ensuring the stability of the orthogonal transformation.

1. Why it is used:
- If a == 0, the orthogonal transformation simplifies since there is no contribution from the first component (a).
- The cosine and sine values are computed based solely on the second component (b).

2. What it does:
- If b is non-zero, the cosine is set to 0, as there is no contribution from the first component.
- The sine is set to the sign of b to ensure the correct rotation direction based on b.
- The radius is calculated as the absolute value of b, representing the magnitude of the vector after the transformation.

. Importance in the Symmetric Orthogonalization Computation:
- Provides a stable and consistent way to compute the orthogonal transformation when one component of the vector is zero.
- Prevents division by zero or undefined behavior in the orthogonalization process.

{'='*200}
""")
                        self.count_lsqr['sym_ortho_condition_2']=False

            elif abs(b) > abs(a):
                tau = a / b
                sine = np.sign(b) / np.sqrt(1 + tau**2)
                cosine = sine * tau
                radius = b / sine
                if self.calculation:
                    logger.info(f"\nAs absolute of b > absolute of a")
                    logger.info(f"tau = a / b:{tau}")
                    logger.info(f"sine = sign of b / square root of (1 + tau^2):{sine}")
                    logger.info(f"cosine = sine * tau:{cosine}")
                    logger.info(f"radius = b / sine:{radius}\n")
                    if self.count_lsqr['sym_ortho_condition_3']:
                        logger.info(f"""
{'='*200}

The purpose of this case is to handle the situation where the second component (b) is larger in magnitude than the first component (a), ensuring the stability and correctness of the orthogonal transformation.

1. Why it is used:
- If |b| > |a|, the transformation is adjusted to avoid numerical instability and to ensure accurate rotation.
- The calculation of the sine and cosine values takes into account the larger value (b) to maintain numerical stability.

2. What it does:
- `tau` is calculated as the ratio of a and b to create a scaling factor for the rotation.
- `sine` is computed as the sign of b divided by the square root of (1 + tau^2), ensuring the proper direction of the rotation.
- `cosine` is then computed as the product of sine and tau, which provides the cosine component of the rotation.
- `radius` is computed as b divided by sine, giving the magnitude of the transformed vector.

3. Importance in the Symmetric Orthogonalization Computation:
- This calculation ensures the orthogonal transformation is stable and efficient when one component is larger than the other.
- Prevents overflow or undefined behavior by carefully computing the trigonometric components and the radius.
- Allows the transformation to handle cases where b is larger than a, a critical part of the Givens rotation process.

{'='*200}
""")
                        self.count_lsqr['sym_ortho_condition_3']=False

            else:
                tau = b / a
                cosine = np.sign(a) / np.sqrt(1 + tau**2)
                sine = cosine * tau
                radius = a / cosine
                if self.calculation:
                    logger.info(f"tau = b / a:{tau}\n")
                    logger.info(f"cosine = sign of a / square root of (1 + tau^2):{cosine}")
                    logger.info(f"sine = cosine * tau:{sine}")
                    logger.info(f"radius = a / cosine:{radius}\n")
                    if self.count_lsqr['sym_ortho_condition_4']:
                        logger.info(f"""

As absolute of a >= absolute of b
tau = b / a:{tau}
cosine = sign of a / square root of (1 + tau^2):{cosine}
sine = cosine * tau:{sine}
radius = a / cosine:{radius}

{'='*200}

The purpose of this case is to handle the situation where the first component (a) is larger or equal in magnitude compared to the second component (b), ensuring the stability and correctness of the orthogonal transformation.

1. Why it is used:
- If |a| >= |b|, the transformation is adjusted to avoid numerical instability and to ensure accurate rotation.
- The calculation of the sine and cosine values is done with respect to the larger value (a) to maintain numerical stability.

2. What it does:
- `tau` is calculated as the ratio of b and a to create a scaling factor for the rotation.
- `cosine` is computed as the sign of a divided by the square root of (1 + tau^2), ensuring the proper direction of the rotation.
- `sine` is then computed as the product of cosine and tau, which gives the sine component of the rotation.
- `radius` is computed as a divided by cosine, giving the magnitude of the transformed vector.

3. Importance in the Symmetric Orthogonalization Computation:
- This calculation ensures the orthogonal transformation is stable and efficient when one component is larger or equal to the other.
- Prevents overflow or undefined behavior by carefully computing the trigonometric components and the radius.
- Handles cases where a is larger than b, a critical part of the Givens rotation process.

{'='*200}
""")
                        self.count_lsqr['sym_ortho_condition_4']=False

            return cosine, sine, radius

        except Exception as e:
            raise RuntimeError(f"An error occurred in __sym_ortho: {e}")


    def __svd_solver(self, X, y):
        X, y = np.asarray(X), np.asarray(y)

        if X.shape[0] != y.shape[0]:
            raise ValueError("The number of rows in X must match the length of y.")

        if self.alpha < 0:
            raise ValueError("Regularization parameter alpha must be non-negative.")

        if y.ndim == 1:
            y = y[:, np.newaxis]

        if self.calculation:
            logger.info("\n<--------------------------------------Ftting using SVD method-------------------------------------->\n")

        if self.fit_intercept:
            X_mean, y_mean = np.mean(X, axis=0), np.mean(y, axis=0)
            X_centered, y_centered = X - X_mean, y - y_mean
            
            if self.calculation:
                logger.info("Applying Mean Centering (AS fit_intercept = True)")
                logger.info(f"X_mean: \n{X_mean}\n")
                logger.info(f"y_mean: \n{y_mean}\n")
        else:
            X_mean, y_mean = np.zeros(X.shape[1]), np.zeros(y.shape[1])
            X_centered, y_centered = X, y
            
            if self.calculation:
                logger.info("Not applying Mean Centering (AS fit_intercept = False)")
                logger.info(f"X_mean: \n{X_mean}\n")
                logger.info(f"y_mean: \n{y_mean}\n")

        if self.calculation:
            logger.info(f"Calculating SVD with centered X: \n{X_centered}\n")

        if self.calculation:
            logger.info(f"Calculating SVD with: \n{X}\n")

        U, S, Vt = self.__svd(X_centered)
        if self.calculation:
            logger.info("\nAfter Computed of SVD:")
            logger.info(f"U: \n{U}\n")
            logger.info(f"S: \n{S}\n")
            logger.info(f"Vt: \n{Vt}\n")

        if S.ndim != 1 or U.shape[0] != X.shape[0] or Vt.shape[0] != S.shape[0]:
            raise ValueError("SVD output dimensions are inconsistent with input matrix X.")

        S_diag = np.diag(1 / (S**2 + self.alpha)) @ np.diag(S)
        if self.calculation:
            logger.info(f"Squaring the S:\n{S**2}\n")
            logger.info(f"Adding alpha with S^2:\n{S**2 + self.alpha}\n")
            logger.info(f"Taking the reciprocal of it:\n{1 / (S**2 + self.alpha)}\n")
            logger.info(f"Taking the diagonal elements of the reciprocal:\n{np.diag(1 / (S**2 + self.alpha))}\n")
            logger.info(f"S_diag = Multiplication between the diagonal elements of the reciprocal and the diagonal elements of S:\n{S_diag}\n")

        self.weights = Vt.T @ S_diag @ (U.T @ y_centered)
        if self.calculation:
            logger.info(f"Multiplying Transpose of Vt and S_diag:\n{Vt.T @ S_diag}\n")
            logger.info(f"Multiplying Transpose of U and y:\n{U.T @ y}\n")
            logger.info(f"Calculating the weights by multiplying the previous 2 results:\n{self.weights}\n")

        self.bias = y_mean - X_mean @ self.weights if self.fit_intercept else np.zeros(y.shape[1])
        if self.calculation:
            if self.fit_intercept:
                logger.info(f"Final Bias => y_mean - (X_mean @ weights): \n{self.bias}\n")
            else:
                logger.info(f"Final Bias => Zero matrix with shape {1}, {y.shape[1]}\n")


    def __svd(self, a):
        if a.ndim != 2:
            raise ValueError("Input matrix must be 2D.")

        if self.calculation:
            logger.info("\n<--------------------------------------Computing SVD-------------------------------------->\n")

        m, n = a.shape

        at_a = np.dot(a.T, a)
        a_at = np.dot(a, a.T)

        if self.calculation:
            logger.info(f"Computing A^T * A:\n{at_a}\n")
            logger.info(f"Computing A * A^T:\n{a_at}\n")


        eigenvalues_v, vh = np.linalg.eigh(at_a)

        if self.calculation:
            logger.info(f"Computing eigenvalues of A^T * A (these correspond to the squared singular values):\n{eigenvalues_v}\n")
            logger.info(f"Computing eigenvectors of A^T * A (columns of V^T):\n{vh}\n")


        eigenvalues_v = np.maximum(eigenvalues_v, 0)

        if self.calculation:
            logger.info(f"Corrected eigenvalues to be non-negative (handling numerical errors):\n{eigenvalues_v}\n")

        sorted_indices_v = np.argsort(eigenvalues_v)[::-1]
        eigenvalues_v = eigenvalues_v[sorted_indices_v]
        vh = vh[:, sorted_indices_v]

        eigenvalues_u, u = np.linalg.eigh(a_at)

        if self.calculation:
            logger.info(f"Sorted eigenvalues and their corresponding eigenvectors in descending order:\n{eigenvalues_v}\n\n{vh}\n")
            logger.info(f"Computing eigenvalues of A * A^T (these correspond to the squared singular values):\n\n{eigenvalues_u}\n")
            logger.info(f"Computing eigenvectors of A * A^T (columns of U):\n{u}")

        eigenvalues_u = np.maximum(eigenvalues_u, 0)
        sorted_indices_u = np.argsort(eigenvalues_u)[::-1]
        eigenvalues_u = eigenvalues_u[sorted_indices_u]
        u = u[:, sorted_indices_u]
        singular_values = np.sqrt(eigenvalues_v)

        if self.calculation:
            logger.info(f"Corrected eigenvalues to be non-negative (handling numerical errors):\n{eigenvalues_u}\n")
            logger.info(f"Sorted eigenvalues and their corresponding eigenvectors in descending order:\n{eigenvalues_u}\n\n{u}\n")
            logger.info(f"Computing singular values as the square root of sorted eigenvalues:\n{singular_values}\n")

        nonzero_singular_values = singular_values > 1e-10
        singular_values = singular_values[nonzero_singular_values]
        vh = vh[:, nonzero_singular_values]

        if self.calculation:
            logger.info(f"Filtered out small singular values and corresponding vectors:\n{singular_values}\n\n{vh}\n")

        u = np.dot(a, vh) / singular_values

        if self.calculation:
            logger.info(f"Computing U by normalizing (A * V) with singular values:\n{u}\n")

        u = np.nan_to_num(u)

        if self.calculation:
            logger.info(f"Replaced NaN values in U with zeros:\n{u}\n")

        return u, singular_values, vh.T


    def __mbsag_solver(self, X, y):
        if self.calculation:
            logger.info("\n<--------------------------------------Ftting using MBSAG method-------------------------------------->\n")
        m, n = X.shape
        if self.max_iter is None:
            if max(m, n)<30:
                self.max_iter = max(m, n) * 5
            else:
                self.max_iter = max(m, n)

        y = y.reshape(-1, 1) if y.ndim == 1 else y
        n_targets = y.shape[1]

        if self.calculation:
            if X.shape[0]>10:
                logger.info("\n**Notice** Showing only first 10 rows to minimize the output size\n")
                logger.info(f"\nGiven X:\n{X[:10]}\n")
                logger.info(f"Given y:\n{y[:10]}\n")
            else:
                logger.info(f"\nGiven X:\n{X}\n")
                logger.info(f"Given y:\n{y}\n")

        self.weights = np.zeros((n, n_targets))

        if self.fit_intercept:
            self.bias = np.zeros(n_targets)
            if self.calculation:
                logger.info(f"Initializing bias as a zero vector of size {n_targets} (AS fit_intercept = True)\n")
        else:
            self.bias = None
            if self.calculation:
                logger.info(f"Bias is not initialized(AS fit_intercept = False)\n")

        gradient_memory = np.zeros((m, n, n_targets))
        avg_gradient = np.zeros((n, n_targets))

        best_loss = float('inf')
        patience_counter = 0

        indices = np.arange(m)

        for epoch in range(self.max_iter):
            start_time = time.time()

            np.random.shuffle(indices)
            X_shuffled, y_shuffled = X[indices], y[indices]

            if self.calculation and (epoch<3 or epoch==self.max_iter-1):
                logger.info("\n**Notice** Showing only first 3 epochs and the last epoch to minimize the output size\n")
                logger.info(f"\nEpoch {epoch + 1} of {self.max_iter}:")
                logger.info(f"{'=' * 50}\n")
                if X.shape[0]>10:
                    logger.info("\n**Notice** Showing only first 10 rows to minimize the output size\n")
                    logger.info(f"Shufflying the X and y:\n{X_shuffled[:10]}\n\n{y_shuffled[:10]}\n")
                else:
                    logger.info(f"Shufflying the X and y:\n{X_shuffled}\n\n{y_shuffled}\n")

            epoch_loss = 0
            correct_predictions = 0

            for j in range(0, m, self.batch_size):
                batch_indices = indices[j:j + self.batch_size]
                X_batch = X_shuffled[j:j + self.batch_size]
                y_batch = y_shuffled[j:j + self.batch_size]

                if self.calculation and (epoch<3 or epoch==self.max_iter-1):
                    logger.info(f"Batch {j // self.batch_size + 1} of {(m // self.batch_size)+1}:")
                    logger.info(f"{'=' * 50}\n")
                    logger.info(f"X_batch:\n{X_batch}\n")
                    logger.info(f"y_batch:\n{y_batch}\n\n")
                    logger.info(f"Now, Computing Prediction with X_batch:")

                y_pred = self.predict(X_batch)
                if self.calculation and (epoch<3 or epoch==self.max_iter-1):
                    logger.info(f"Predictions:\n{y_pred}\n")
                    logger.info(f"Now, Computing Prediction with X_batch, y_batch and computed predictions\n")
                gradients = self.__compute_gradients(X_batch, y_batch, y_pred)

                if self.calculation and (epoch<3 or epoch==self.max_iter-1):
                    logger.info(f"Gradients of weights (Transpose of X @ (y_pred - y) / no. of rows in X):\n{gradients['weights']}\n")
                    logger.info(f"Gradients of bias (mean of (y_pred - y)):\n{gradients['bias']}\n")

                for idx, sample_idx in enumerate(batch_indices):
                    sample_gradient = gradients['weights']
                    avg_gradient += (sample_gradient - gradient_memory[sample_idx]) / m
                    gradient_memory[sample_idx] = sample_gradient

                    if self.calculation and idx<2 and (epoch<3 or epoch==self.max_iter-1):
                        logger.info("\n**Notice** Showing only first 2 iteration to minimize the output size\n")
                        logger.info(f"Iteraton {idx+1} of 2:\n")
                        logger.info(f"{'=' * 50}\n")
                        logger.info(f"Sample Gradient(gradients['weights']):\n{sample_gradient}\n")
                        logger.info(f"Updated Avgerage Gradient((sample_gradient - gradient_memory[sample_idx]) / no. of rows in X):\n{avg_gradient}\n")
                        logger.info(f"**Notice** Showing only the part where Gradient Memory has updated to minimize the output size")
                        logger.info(f"Updated Gradient Memory of {sample_idx} position (sample_gradient):{gradient_memory[sample_idx]}\n")

                self.weights -= self.alpha * avg_gradient

                if self.calculation and (epoch<3 or epoch==self.max_iter-1):
                    if X.shape[0]>10:
                        logger.info("\nShowing only first 10 rows to minimize the output size\n")
                        logger.info(f"Updated Weights(weights - (alpha * avg_gradient)):\n{self.weights[:10]}\n")
                    else:
                        logger.info(f"Updated Weights(weights - (alpha * avg_gradient)):\n{self.weights[:10]}\n")

                if self.fit_intercept:
                    avg_bias_gradient = -np.mean(y_batch - y_pred, axis=0)
                    self.bias -= self.alpha * avg_bias_gradient

                    if self.calculation and (epoch<3 or epoch==self.max_iter-1):
                        if X.shape[0]>10:
                            logger.info("\nShowing only first 10 rows to minimize the output size\n")
                            logger.info(f"Average Bias Gradient(mean of (y_batch - y_pred)):\n{avg_bias_gradient[:10]}\n")
                            logger.info(f"Updated Bias(bias - (alpha * avg_bias_gradient)):\n{self.bias[:10]}\n")
                        else:
                            logger.info(f"Average Bias Gradient(mean of (y_batch - y_pred)):\n{avg_bias_gradient}\n")
                            logger.info(f"Updated Bias(bias - (alpha * avg_bias_gradient)):\n{self.bias}\n")

                if self.verbose:
                    batch_loss = self.__compute_loss(X_batch, y_batch)
                    epoch_loss += batch_loss * len(X_batch)
                    predicted_labels = (y_pred >= 0.5).astype(int)
                    correct_predictions += np.sum(predicted_labels == y_batch)

            try:
                self.history.append((self.weights.copy(), self.bias.copy() if self.fit_intercept else 0))
            except Exception as e:
                logger.error(f"\033[91mAn Error during history update: {e} \033[0m")
                continue

            if self.verbose:
                try:
                    epoch_loss /= m
                    val_loss = self.__compute_loss(X, y)

                    predicted_labels_full = (self.predict(X) >= 0.5).astype(int)
                    epoch_r2_score = self.__compute_r2_score(y, predicted_labels_full)
                    epoch_r2_score = epoch_r2_score if epoch_r2_score is not None else 0.0

                    epoch_mae = np.mean(np.abs(y - predicted_labels_full))
                    epoch_mse = np.mean((y - predicted_labels_full) ** 2)
                    epoch_rmse = np.sqrt(np.mean((y - predicted_labels_full) ** 2))

                    end_time = time.time()
                    logger.info(
                        f"Epoch {epoch + 1}/{self.max_iter} - {m // self.batch_size}/{m // self.batch_size} "
                        f"[{'=' * 25}] - {end_time - start_time:.1f}s "
                        f"{(end_time - start_time) / (m // self.batch_size):.2f}ms/step - "
                        f"loss: {epoch_loss:.4f} - mae: {epoch_mae:.4f} - "
                        f"mse: {epoch_mse:.4f} - rmse: {epoch_rmse:.4f} - "
                        f"r2_score: {epoch_r2_score:.4f} - val_loss: {val_loss:.4f}"
                    )
                except Exception as e:
                    logger.info(f"\033[91mAn Error during verbose output: {e} \033[0m")
                    continue

            if self.early_stopping:
                try:
                    val_loss = self.__compute_loss(X, y)

                    if self.calculation:
                        logger.info(f"Validation Loss: {val_loss}\n")

                    if val_loss < best_loss - self.tol:
                        best_loss = val_loss
                        patience_counter = 0

                        if self.calculation:
                            logger.info("As Validation Loss < (Best Loss - tolarance)")
                            logger.info("Best Loss = Validation Loss")
                            logger.info("Patience Counter = 0\n")

                    else:
                        patience_counter += 1
                        if self.calculation:
                            logger.info(f"As Validation Loss >= (Best Loss - tolarance)")
                            logger.info(f"Patience Counter = {patience_counter}\n")

                    if patience_counter >= self.patience:
                        logger.info(f"Early stopping at iteration {epoch + 1}. No improvement in loss for {self.patience} iterations.\n\n")
                        if self.calculation:
                            logger.info(f"AS Patience Counter has reached its limit\nENDING THE FITTING PROCESS!!!\n")
                        break
                except Exception as e:
                    logger.error(f"\033[91mAn Error during early stopping check: {e} \033[0m")
                    break


    def __compute_r2_score(self, y_true, y_pred):
        total_variance = np.sum((y_true - np.mean(y_true)) ** 2)
        residual_variance = np.sum((y_true - y_pred) ** 2)
        r2_score = 1 - (residual_variance / (total_variance + 1e-9))
        return r2_score


    def __compute_gradients(self, X, y, y_pred):
        gradients_w = X.T @ (y_pred - y) / X.shape[0]
        gradients = {'weights': gradients_w}
        if self.fit_intercept:
            gradients_b = np.mean(y_pred - y, axis=0)
            gradients['bias'] = gradients_b
        return gradients


    def __compute_loss(self, X, y):
        predictions = self.predict(X)
        loss = np.mean(np.sum((y - predictions) ** 2, axis=1))
        return loss


    def __cholesky_solver(self, X, y):
        X, y = np.asarray(X), np.asarray(y)

        if not np.all(np.isfinite(X)) or not np.all(np.isfinite(y)):
            raise ValueError("Input contains NaN or infinite values.")
        if self.alpha <= 0:
            raise ValueError("Regularization parameter alpha must be positive.")

        if self.calculation:
            logger.info("\n<--------------------------------------Ftting using Cholesky method-------------------------------------->\n")

        if self.calculation:
            if X.shape[0]>10:
                logger.info("\n**Notice** Showing only first 10 rows to minimize the output size\n")
                logger.info(f"\nGiven X:\n{X[:10]}\n")
                logger.info(f"Given y:\n{y[:10]}\n")
            else:
                logger.info(f"\nGiven X:\n{X}\n")
                logger.info(f"Given y:\n{y}\n")

        if self.fit_intercept:
            X_mean = np.mean(X, axis=0)
            X -= X_mean
            y_mean = np.mean(y)
            y -= y_mean

            if self.calculation:
                logger.info("Applying Mean Centering (AS fit_intercept = True)")
                logger.info(f"X_mean: \n{X_mean}\n")
                logger.info(f"y_mean: \n{y_mean}\n")
        else:
            y_mean = 0

            if self.calculation:
                logger.info(f"y_mean = 0\n")

        XTX = X.T @ X
        XTy = X.T @ y

        if self.calculation:
            if XTX.shape[0]>10:
                logger.info("\n**Notice** Showing only first 10 rows to minimize the output size\n")
                logger.info(f"XTX = Transpose of X @ X:\n{XTX[:10]}\n")
                logger.info(f"XTy = Transpose of X @ y:\n{XTy[:10]}\n")
            else:
                logger.info(f"XTX = Transpose of X @ X:\n{XTX}\n")
                logger.info(f"XTy = Transpose of X @ y:\n{XTy}\n")

        regularization_matrix = self.alpha * np.eye(X.shape[1])
        A = XTX + regularization_matrix

        if self.calculation:
            if A.shape[0]>10:
                logger.info("\n**Notice** Showing only first 10 rows to minimize the output size\n")
                logger.info(f"Regularization Matrix (alpha * I):\n{regularization_matrix[:10]}\n")
                logger.info(f"A = XTX + alpha * I:\n{A[:10]}\n")
            else:
                logger.info(f"Regularization Matrix (alpha * I):\n{regularization_matrix}\n")
                logger.info(f"A = XTX + alpha * I:\n{A}\n")

        n = A.shape[0]
        L = np.zeros_like(A)

        if self.calculation:
            logger.info(f"Initializing L as a zero matrix of size {n} x {n}\n")

        for i in range(n):
            if self.calculation:
                logger.info(f"\nIteraton {i+1} of {n}")
                logger.info(f"{'=' * 30}\n")
            for j in range(i + 1):
                if i == j:
                    sum_diagonal = np.sum(L[i, :j]**2)
                    value = A[i, i] - sum_diagonal
                    if value <= 0:
                        raise ValueError(f"Matrix is not positive definite at index ({i}, {i}).")
                    L[i, i] = np.sqrt(value)

                    if self.calculation:
                        logger.info(f"\nSub-iteraton {j+1} of {i+1}")
                        logger.info(f"{'=' * 70}\n")
                        logger.info(f"L[{i}, {i}] = sqrt(A[{i}, {i}] - sum(L[{i}, :{j}]^2)): {L[i, i]}\n")
                else:
                    sum_off_diagonal = np.sum(L[i, :j] * L[j, :j])
                    if L[j, j] == 0:
                        raise ZeroDivisionError(f"Zero encountered on the diagonal at index {j}.")
                    L[i, j] = (A[i, j] - sum_off_diagonal) / L[j, j]

                    if self.calculation:
                        logger.info(f"\nSub-iteraton {j+1} of {i+1}")
                        logger.info(f"{'=' * 70}\n")
                        logger.info(f"L[{i}, {j}] = sqrt(A[{i}, {j}] - sum(L[{i}, :{j}] * L[{j}, :{j}])): {L[i, j]}\n")


        self.weights = np.linalg.solve(L.T, np.linalg.solve(L, XTy))
        self.bias = y_mean - np.dot(X_mean, self.weights) if self.fit_intercept else 0

        if self.calculation:
            logger.info(f"\nFinal Weights(np.linalg.solve(L.T, np.linalg.solve(L, XTy))):\n{self.weights}\n")
            logger.info(f"Final Bias(y_mean - np.dot(X_mean, self.weights) if self.fit_intercept else 0):\n{self.bias}\n")


    def __getattribute__(self, name):
        try:
            if name.startswith("_RidgeRegression__"):
                return super().__getattribute__(name)
        except Exception as e:
            logger.error(f"\033[91mAn Error in internal calls to private methods in __getattribute__: {e}\033[0m")
            raise

        try:
            if name in [
                "mbsag_solver", "svd_solver", "lsqr_solver", "cholesky_solver",
                "svd", "lsqr", "compute_r2_score", "compute_gradient",
                "compute_loss", "sym_ortho",
                "__mbsag_solver", "__svd_solver", "__lsqr_solver", "__cholesky_solver",
                "__svd", "__lsqr", "__compute_r2_score",
                "__compute_gradient", "__compute_loss", "__sym_ortho",
                "_RidgeRegression__mbsag_solver", "_RidgeRegression__svd_solver",
                "_RidgeRegression__lsqr_solver", "_RidgeRegression__cholesky_solver",
                "_RidgeRegression__compute_r2_score", "_RidgeRegression__compute_gradient",
                "_RidgeRegression__compute_loss",
                "_RidgeRegression__svd", "_RidgeRegression__sym_ortho", "_RidgeRegression__lsqr"
            ]:
                logger.error(f"\033[91mAccess to '{name}' is restricted for some reasons.\033[0m")

                logger.info(f"\033[92mBut you can get the information and detailed explanation about {name} from model_analysis method. Here's how you can use it:\033[0m")
                logger.info("\033[92mmodel = RidgeRegression()\033[0m")
                logger.info(f"\033[92mmodel.model_analysis('{name}')\n\n\033[0m")

                raise AttributeError

            return super().__getattribute__(name)

        except AttributeError:
            return None

        except Exception as e:
            logger.error(f"\033[91mAn Error in direct or indirect access to restricted methods: {e}\033[0m")
            raise


    def model_analysis(self,doc_name=None):
        """
        this method returns a detailed explanation or method based on the given `doc_name`.

        This method is used to retrieve specific methods or explanations based on the provided `doc_name` string.
        The method matches the `doc_name` against various predefined options, each representing a specific solver, algorithm, or function used in this class.
        If the `doc_name` is not recognized, an exception is raised.


        Parameters:
        -----------
        doc_name : str
            A string representing the name of the method or explanation to be returned. 
            You can pass the standard name (e.g., 'lsqr_solver') or the internal method name (e.g., '__lsqr_solver').
            
            - 'lsqr_solver': Provides a detailed explanation of the LSQR solver implementation for Ridge Regression.
            - 'lsqr': Provides the mathematical details of the LSQR algorithm used for solving sparse linear systems.
            - 'sym_ortho': Explains the Symmetric Orthogonalization Computation used to maintain stability in LSQR.
            - 'svd_solver': Provides a detailed explanation of the Singular Value Decomposition (SVD) solver implementation.
            - 'svd': Explains the mathematical concepts behind Singular Value Decomposition.
            - 'mbsag_solver': Provides a detailed explanation of the Mini-Batch Stochastic Average Gradient solver.
            - 'cholesky_solver': Explains the Cholesky Decomposition solver implementation.
            - 'compute_r2_score': Explains the mathematical formula and implementation of the R² score metric.
            - 'compute_gradient': Detials how gradients for weights and bias are computed during optimization.
            - 'compute_loss': Explains the Ridge Regression loss function (MSE with L2 Regularization).
            - 'adv_lim': Provides an overview of the advantages and limitations of Ridge Regression.

        Returns:
        --------
        method or explanation (varies based on `doc_name`):
            Depending on the `doc_name` provided, if the `doc_name` matches, the corresponding method or explanation is returned.

        Raises:
        -------
        ValueError:
            If the `doc_name` is `None` or does not match any of the predefined options,
            a `ValueError` is raised with an appropriate error message.

        Example:
            >>> from mlmechanica.regression.linear import RidgeRegression
            >>> model = RidgeRegression()
            >>> print(model.model_analysis('lsqr'))

        """

        try:
            lsqr_solver = textwrap.dedent("""
        This method implements a regularized least squares solver using the LSQR method for linear regression.
        It is part of a class that models multivariate linear regression with L2 regularization (Ridge Regression).
        The method includes support for handling intercepts and multivariate outputs.

        Parameters:
        -----------
        - X: numpy.ndarray
            Input feature matrix of shape (m, n), where m is the number of samples
            and n is the number of features.
        - y: numpy.ndarray
            Target values of shape (m, 1) for single output or (m, k) for multiple outputs.

        Returns:
        --------
        - Updates the instance with the computed weights and biases.

        Raises:
        -------
        - ValueError: If `X` and `y` dimensions do not align.
        - AttributeError: If required attributes (fit_intercept, alpha) are missing.
        - RuntimeError: If any issue occurs during computation.


        Theoretical Explanation
        =======================

        Linear Regression
        -----------------
        Linear regression models the relationship between input features `X` and target values `y` using the equation:
            y = Xw + b
        where:
        - `X` is the design matrix of shape (m, n), with `m` samples and `n` features.
        - `w` is the weight vector (or coefficients) of shape (n, 1).
        - `b` is the bias term (intercept).


        Least Squares Estimation
        ------------------------
        To estimate `w`, we minimize the sum of squared residuals:
            min_w ||y - Xw||^2


        L2 Regularization
        -----------------
        To prevent overfitting and handle multicollinearity, L2 regularization is added:
            min_w ||y - Xw||^2 +  alpha ||w||^2
        where:
        -  alpha  is the regularization parameter controlling the penalty term.

        The closed-form solution is:
            w = (XᵀX +  alpha I)⁻¹Xᵀy
        where `I` is the identity matrix of shape (n, n).


        Multivariate Outputs
        --------------------
        For multivariate outputs (y with multiple columns), the solution generalizes to compute `w` for each output column independently.


        Method Details
        ==============

        This method implements this process step-by-step, ensuring compatibility with the following:
        1. Data pre-processing: Handles input validation, dimensionality checks, and centering.
        2. Regularization: Adds L2 regularization (controlled by `alpha`).
        3. Multivariate Outputs: Solves for weights iteratively for each output column in `y`.
        4. Fit Intercept: Centers `X` and `y` if `fit_intercept` is enabled.
        """).strip()

            lsqr=textwrap.dedent("""
        This method implements the LSQR (Least Squares QR) algorithm for solving linear systems of the form:
            Ax = b
        where:
        - `A` is a matrix (linear operator).
        - `x` is the solution vector.
        - `b` is the right-hand side vector.

        The method includes support for handling regularization (damping) and iterative solution updates,
        with an optional initial guess for the solution.

        Parameters:
        -----------
        - A: linear operator or numpy.ndarray
            The matrix or linear operator representing the system `A`. It should be a 2D matrix of shape (m, n),
            where `m` is the number of rows and `n` is the number of columns.
        - b: numpy.ndarray
            The right-hand side vector of shape (m,), representing the target values of the system.
        - damp: float
            The regularization (damping) parameter used to control the strength of regularization. A non-negative value.
        - x0: numpy.ndarray, optional (default=None)
            The initial guess for the solution vector `x` of shape (n,). If not provided, the solution is initialized to zeros.
        - max_iter: int, optional (default=None)
            The maximum number of iterations for the LSQR algorithm. If None, the iteration limit is set to 2 * min(m, n).

        Returns:
        --------
        - solution: numpy.ndarray
            The computed solution vector `x` of shape (n,) that minimizes the least squares problem.

        Raises:
        -------
        - ValueError: If the dimensions of `A` and `b` do not match or if invalid parameters are passed.
        - RuntimeError: If any error occurs during matrix-vector operations or orthogonalization steps.
        - Exception: For any other unexpected errors during the computation.


        Theoretical Explanation
        ========================

        The LSQR algorithm is an iterative method used to solve the linear system `Ax = b`.
        It is particularly useful for large and sparse matrices. The method is based on the bidiagonalization of the matrix `A`
        and uses a least-squares approach to find the solution.

        The algorithm updates the solution `x` iteratively by minimizing the residual `r = b - Ax`
        and adjusting the direction based on the residual and the damping term. The damping term is used to regularize the solution
        and avoid overfitting or instability in the case of ill-conditioned problems.

        The key steps of the LSQR algorithm are:
        1. Residual Calculation:
        - The residual is computed as `r = b - Ax`, and its norm is calculated.
        2. Direction Calculation:
        - A direction vector is determined by applying the transpose of the matrix `A` to the residual.
        3. Iteration:
        - The residual and direction are iteratively updated. The solution is refined in each step by adding a scaled version of the direction vector.
        - At each iteration, a symmetric orthogonalization process is applied to update the residual and direction vectors.
        4. Regularization (Damping):
        - The damping parameter is used to control the magnitude of the updates and prevent overfitting.


        Method Details
        ==============

        This method follows these steps:

        1. Input Validation:
        - The matrix `A` is converted to a linear operator using `aslinearoperator`, and the vector `b` is reshaped if necessary.
        - Validates that `A` and `b` are compatible in dimensions.

        2. Initialization:
        - Initializes the residual as `b`, computes its norm, and optionally initializes the solution vector `x` (if `x0` is provided).
        - Initializes other necessary values such as direction, damping, and iteration parameters.

        3. Main Iteration Loop:
        - Performs iterations to refine the solution. In each iteration:
            - The residual is updated by applying `A` and its transpose.
            - The direction is calculated and normalized.
            - Regularization and damping are applied if necessary.
            - A symmetric orthogonalization step is performed to update the residual and direction.
            - The solution is updated using the current step.

        4. Convergence Check:
        - The iteration continues until the maximum number of iterations (`max_iter`) is reached, or until the norm of the residual is sufficiently small.

        5. Solution Return:
        - The final solution is returned after completing the iterative process.


        Mathematical Background
        =======================

        Problem Statement
        -----------------
        Given a system:
            Ax ≈ b
        the goal is to find `x` such that:
            ||Ax - b||^2
        is minimized.
        Here:
        - `A` is a matrix of size (m, n),
        - `b` is a vector of size (m,),
        - `x` is the solution vector of size (n,).

        For regularized least-squares problems, we add an L2 regularization term:
            min_x ||Ax - b||^2 + damp^2 ||x||^2
        where `damp` is a scalar parameter controlling the regularization.


        Iterative Solution Approach
        ---------------------------
        LSQR provides an iterative solution to the least-squares problem by progressively improving the solution vector `x`.
        At each iteration, the residual vector `r` is updated, and an updated direction vector `d` is used to make a step toward the solution.

        The key operations performed at each iteration include:
        1. Matrix-vector products: The algorithm applies the matrix `A` to the current direction and updates the residual vector.
        2. Symmetric orthogonalization: To maintain numerical stability and ensure convergence, Givens rotations are used to orthogonalize vectors at each step.
        3. Solution update: The solution is updated using the computed step size, and the direction vector is also updated to maintain convergence toward the least-squares solution.


        Convergence and Stopping Criteria
        ---------------------------------
        The algorithm iterates until one of the following stopping conditions is met:
        1. The residual norm is sufficiently small:
            ||Ax - b|| / ||b|| < ε
        where `ε` is a user-defined tolerance.
        2. The maximum number of iterations `iter_lim` is reached.

        The convergence is influenced by the regularization parameter `damp`, which helps control the solution's stability by penalizing large values of `x`.


        Regularization and Damping
        --------------------------
        The algorithm allows for regularization of the least-squares problem through the inclusion of a damping factor `damp`.
        The damping term is added to the objective function to avoid overfitting and to stabilize the solution, especially in cases where `A` is ill-conditioned.

        The regularization term is controlled by the square of the damping factor, damp^2.
        At each iteration, the regularization effect is updated to ensure that the solution remains within a feasible range.


        Symmetric Orthogonalization and Givens Rotations
        ------------------------------------------------
        In LSQR, symmetric orthogonalization is performed during each iteration to maintain the orthogonality of vectors, ensuring numerical stability.
        This is achieved by applying Givens rotations, which are 2D rotations that preserve the vector norms.

        Given two scalars `a` and `b`, the Givens rotation is performed by computing cosine and sine values that are used to eliminate off-diagonal terms,
        ultimately leading to orthogonal residual and direction vectors. This is done using the following relations:
            cos(θ), sin(θ), rho

        This ensures that each new residual is orthogonal to the previous one, and that the solution vector converges towards the optimal least-squares solution.


        Mathematical Equations in algorithm
        -----------------------------------
        1. Matrix-vector operations: At each iteration, the matrix-vector product is performed:
            r = b - A x
            and updated as:
            r = A direction - direction_norm * residual

        2. Residual and Direction Update: The direction is updated as:
            direction = A^T residual - residual_norm * direction

        3. Step Size: The solution is updated using:
            x = x + (phi / rho) * step
            where `phi` and `rho` are the quantities computed during symmetric orthogonalization.

        4. Regularization Update: If damping is applied, the regularization norm is updated at each iteration:
            rhobar1 = sqrt(rhobar^2 + damp^2)
            and used to adjust the solution.

        5. Convergence: The algorithm converges when the residual norm satisfies:
            ||r_k|| / ||b|| < ε


        Summary of the Algorithm
        ========================

        Initialization:
        ---------------
        - Start with an initial guess `x0` (or assume zero if none provided).
        - Compute the initial residual: r0 = b - A x0
        - Normalize the residual and compute the initial direction vector.

        Iterative Updates:
        ------------------
        - Update the residual and direction at each iteration by applying matrix-vector operations.
        - Perform symmetric orthogonalization using Givens rotations.
        - Update the solution vector `x` and direction vector.

        Termination:
        ------------
        - The algorithm terminates when the residual norm is small enough or the maximum number of iterations is reached.

        The LSQR algorithm efficiently solves large-scale least-squares problems while maintaining numerical stability through orthogonalization and regularization.
        The damping parameter ensures that the solution does not overfit or grow unbounded, particularly in ill-conditioned systems.
        The iterative process allows for handling sparse or large matrices effectively, making LSQR an important method in scientific computing and data analysis.
        """).strip()

            sym_ortho = textwrap.dedent("""
        This method performs Symmetric Orthogonalization, a technique used to compute the cosine, sine, and radius for a given pair of values `a` and `b`.
        The method calculates these values using a Givens rotation approach, commonly used in numerical linear algebra to zero out certain elements in a matrix.

        Parameters:
        -----------
        - a: float
            The first value used in the orthogonalization process.
        - b: float
            The second value used in the orthogonalization process.

        Returns:
        --------
        - cosine: float
            The cosine value of the Givens rotation.
        - sine: float
            The sine value of the Givens rotation.
        - radius: float
            The radius (or norm) used in the rotation, which is the result of applying the Givens transformation.

        Raises:
        -------
        - RuntimeError: If any error occurs during the computation, such as issues with invalid input.


        Theoretical Explanation
        ========================

        Symmetric Orthogonalization is used to transform a pair of values `(a, b)` into a rotated form where one of the values (usually `b`) is zeroed out. This is done using a Givens rotation, which involves computing the cosine and sine of the rotation, as well as the radius (or norm) of the vector formed by `(a, b)`.

        The Givens rotation matrix is of the form:

            G = [ cos(theta)  sin(theta) ]
                [ -sin(theta) cos(theta) ]

        This rotation matrix is applied to the vector `(a, b)` to transform it into a new vector where one component is zero, with the other representing the radius.

        The rotation is computed based on the following logic:

        1. Case 1: `b == 0`:
        - If `b` is zero, the cosine is the sign of `a`, and the sine is zero. The radius is the absolute value of `a`.

        2. Case 2: `a == 0`:
        - If `a` is zero, the cosine is zero, and the sine is the sign of `b`. The radius is the absolute value of `b`.

        3. Case 3: `abs(b) > abs(a)`:
        - If the absolute value of `b` is greater than the absolute value of `a`, the rotation is computed using the formula for `tau`, sine, cosine, and radius based on `a` and `b`.

        4. Case 4: `abs(a) >= abs(b)`:
        - If the absolute value of `a` is greater than or equal to `b`, the rotation is computed using a similar approach, but with `b` and `a` swapped in the formula.


        Method Details
        ==============

        The method computes the cosine, sine, and radius values for a pair of values `(a, b)` based on the following conditions:

        1. If `b == 0`, it calculates the cosine as the sign of `a` and the sine as zero, with the radius being the absolute value of `a`.
        2. If `a == 0`, it calculates the cosine as zero and the sine as the sign of `b`, with the radius being the absolute value of `b`.
        3. If `abs(b) > abs(a)`, it computes the rotation parameters using `tau = a / b`, and then derives the sine, cosine, and radius.
        4. If `abs(a) >= abs(b)`, it computes the rotation parameters similarly using `tau = b / a`, with corresponding updates to the sine, cosine, and radius.

        Finally, it returns the computed `cosine`, `sine`, and `radius` values.


        Mathematical Background
        =======================
        Symmetric Orthogonalization computes an orthogonal transformation of two scalars `a` and `b` such that:

            [cosine sine] [a] = [radius]
            [-sine cosine] [b] = [  0  ]

        Problem Statement and Goal
        ---------------------------
        Given two scalars `a` and `b`, the goal is to find:
        1. Orthogonal transformation:
            [cosine sine] [a] = [radius]
            [-sine cosine] [b] = [  0  ]

            Here:
            - `cosine` and `sine` define the rotation matrix.
            - `radius = sqrt(a^2 + b^2)`, the Euclidean norm.

        2. Preservation of the vector's norm:
            sqrt(a^2 + b^2) = radius
            The rotation does not change the length of the vector.

        3. Stability:
            Avoid division by small numbers or overflow due to squaring large numbers.


        Intuition Behind the Algorithm
        ------------------------------
        1. Orthogonality and Stability:
        The transformation is orthogonal, meaning:
            [cosine sine]
            [-sine cosine]
        is a rotation matrix that satisfies:
            Q^T Q = I
        This property ensures that the operation preserves numerical precision and the vector's norm.

        2. Eliminating `b`:
        The transformation ensures the second component of the vector becomes zero:
            [r]
            [0]
        This simplifies many iterative computations like QR decomposition and LSQR.

        3. Efficiency:
        Instead of directly calculating angles (theta), which involves computationally expensive trigonometric functions, the algorithm calculates ratios and avoids divisions by small values.


        Detailed Mathematical Derivation
        --------------------------------
        Rotation Transformation
        -----
        The goal is to find:
            cosine, sine, radius = __sym_ortho(a, b)

        such that:
            [cosine sine] [a] = [radius]
            [-sine cosine] [b] = [  0  ]

        Expanding the above:
            cosine * a + sine * b = r    (1)
            -sine * a + cosine * b = 0   (2)

        From equation (2):
            sine * a = cosine * b
        Rearranging:
            tan(theta) = b / a    (if `a != 0`).

        Using the Pythagorean identity:
            cosine^2 + sine^2 = 1,
        we compute:
            cosine = 1 / sqrt(1 + tan^2(theta)),    sine = tan(theta) * cosine.

        Radius (`r`)
        -----
        From equation (1):
            r = sqrt((cosine * a)^2 + (sine * b)^2)
        Substituting cosine^2 + sine^2 = 1:
            r = sqrt(a^2 + b^2).


        Handling Edge Cases
        -------------------
        1. If `b == 0`:
            - sine = 0, cosine = sign(a), radius = |a|.
            - No rotation is needed since the vector lies along the x-axis.

        2. If `a == 0`:
            - cosine = 0, sine = sign(b), radius = |b|.
            - The vector lies along the y-axis, requiring a 90° rotation.

        3. Numerical Stability:
            - The algorithm chooses whether to compute ratios `a / b` or `b / a`, depending on their magnitudes, to avoid division by small numbers.


        Geometric Intuition
        -------------------
        1. Rotation to the Axis:
        The algorithm rotates the vector `(a, b)` to align it with the x-axis. The "radius" `r` is the magnitude of the vector:
            r = sqrt(a^2 + b^2).

        2. Role of `cosine` and `sine`:
        These values define the "direction" of the vector in terms of the rotation matrix. By computing `tan(theta) = b / a`, the algorithm finds the angle `theta` that brings `b` to zero.


        Practical Applications
        ----------------------
        1. Numerical Stability:
        The algorithm ensures that operations like QR decomposition or bidiagonalization are stable, avoiding loss of precision due to ill-conditioned matrices.

        2. Iterative Solvers:
        In methods like LSQR, orthogonal transformations simplify the least-squares problem without explicitly forming the normal equations.

        3. Generalized Eigenvalue Problems:
        Symmetric orthogonalization is critical in reducing a matrix to simpler forms, like Hessenberg or bidiagonal forms, for eigenvalue computation.

        By relying on the geometric intuition of rotations and rigorous mathematical derivation, the symmetric orthogonalization algorithm is a powerful tool for numerical linear algebra.
        """).strip()

            svd_solver = textwrap.dedent("""
        This method implements a solver for ridge regression using the Singular Value Decomposition (SVD) technique.
        It is part of a class that models multivariate linear regression with L2 regularization (Ridge Regression).
        The method handles intercepts and supports multivariate outputs.

        Parameters:
        -----------
        - X: numpy.ndarray
            Input feature matrix of shape (m, n), where m is the number of samples
            and n is the number of features.
        - y: numpy.ndarray
            Target values of shape (m, 1) for single output or (m, k) for multiple outputs.

        Returns:
        --------
        - Updates the instance with the computed weights and biases.

        Raises:
        -------
        - ValueError: If:
            - The number of rows in `X` does not match the number of rows in `y`.
            - The regularization parameter `alpha` is negative.
            - The dimensions of the SVD output are inconsistent with the input matrix `X`.
        - Exception: If any other unexpected error occurs during computation.


        Theoretical Explanation
        =======================

        Linear Regression
        -----------------
        Linear regression models the relationship between input features `X` and target values `y` using the equation:
            y = Xw + b
        where:
        - `X` is the design matrix of shape (m, n), with `m` samples and `n` features.
        - `w` is the weight vector (or coefficients) of shape (n, 1).
        - `b` is the bias term (intercept).

        Least Squares Estimation
        ------------------------
        To estimate `w`, we minimize the sum of squared residuals:
            min_w ||y - Xw||^2

        L2 Regularization
        -----------------
        To prevent overfitting and handle multicollinearity, L2 regularization is added:
            min_w ||y - Xw||^2 +  alpha ||w||^2
        where:
        -  alpha  is the regularization parameter controlling the penalty term.

        Using SVD for Ridge Regression
        ------------------------------
        The SVD decomposition of `X` is given by:
            X = UΣVᵀ
        where:
        - `U` is an orthogonal matrix of shape (m, m),
        - `Σ` is a diagonal matrix of shape (min(m, n), min(m, n)) containing singular values,
        - `Vᵀ` is an orthogonal matrix of shape (n, n).

        The ridge regression solution in terms of SVD is:
            w = VΣ⁻¹(Σ² +  alpha I)⁻¹ΣUᵀy
        where:
        - `I` is the identity matrix of appropriate shape,
        - ` alpha ` is the regularization parameter.

        Multivariate Outputs
        --------------------
        For multivariate outputs (y with multiple columns), the solution generalizes to compute `w` for each output column independently.


        Method Details
        ==============

        This method implements this process step-by-step, ensuring compatibility with the following:
        1. Data Pre-processing:
            - Converts input `X` and `y` to numpy arrays.
            - Validates dimensions of `X` and `y`.
            - Handles intercepts by centering `X` and `y` if `fit_intercept` is enabled.
        2. SVD Decomposition:
            - Performs SVD on `X` to decompose it into `U`, `Σ`, and `Vᵀ`.
            - Ensures the output dimensions of SVD are consistent with the input.
        3. Regularization:
            - Computes the diagonal matrix for regularization using `Σ² +  alpha `.
        4. Weight and Bias Calculation:
            - Computes weights `w` using the SVD components and the target `y`.
            - Calculates biases based on the mean of `X` and `y` if `fit_intercept` is enabled.
        5. Error Handling:
            - Catches and raises appropriate exceptions for input validation and computational errors.
        """).strip()

            svd = textwrap.dedent(        """
        This method implements the Singular Value Decomposition (SVD) for a given 2D input matrix.
        It decomposes the matrix into three components: U (left singular vectors), singular values (Σ), and Vᵀ (right singular vectors).
        The method uses eigenvalue decomposition to calculate the singular values and vectors.

        Parameters:
        -----------
        - a: numpy.ndarray
            The input matrix of shape (m, n), where `m` is the number of rows (samples)
            and `n` is the number of columns (features).

        Returns:
        --------
        - u: numpy.ndarray
            The left singular vectors matrix of shape (m, k), where `k` is the rank of the input matrix.
        - singular_values: numpy.ndarray
            A 1D array of singular values of shape (k,), sorted in descending order.
        - vh: numpy.ndarray
            The transpose of the right singular vectors matrix (Vᵀ), of shape (k, n).

        Raises:
        -------
        - ValueError: If the input matrix `a` is not 2D.
        - np.linalg.LinAlgError: If there is a linear algebra issue during eigenvalue decomposition.
        - Exception: If any unexpected error occurs during computation.


        Theoretical Explanation
        =======================

        Singular Value Decomposition (SVD)
        ----------------------------------
        SVD decomposes a matrix `A` (of shape (m, n)) into three matrices:
            A = UΣVᵀ
        Where:
        - `U` is an orthogonal matrix of shape (m, m) containing the left singular vectors.
        - `Σ` is a diagonal matrix of singular values of shape (m, n) with non-negative real numbers along the diagonal.
        - `Vᵀ` is an orthogonal matrix of shape (n, n) containing the right singular vectors (the transpose of `V`).

        The eigenvalue decomposition for computing SVD is as follows:
        1. Compute `AᵀA` and `AAᵀ` which are square matrices:
            - `AᵀA` has eigenvalues corresponding to the squared singular values.
            - `AAᵀ` has eigenvalues corresponding to the same singular values.

        2. Calculate the eigenvalues and eigenvectors for both `AᵀA` and `AAᵀ`:
            - The eigenvectors of `AᵀA` form the columns of `V`.
            - The eigenvectors of `AAᵀ` form the columns of `U`.

        3. The singular values are the square roots of the eigenvalues from `AᵀA`.

        4. The singular vectors and values are ordered such that the singular values are in descending order.


        Method Details
        ==============

        This method implements the SVD computation using the following steps:
        1. Input Validation:
            - Converts the input matrix `a` to a numpy array.
            - Checks that the input matrix `a` is 2-dimensional.
        2. Eigenvalue Decomposition:
            - Computes the eigenvalues and eigenvectors of `AᵀA` and `AAᵀ`.
            - Ensures eigenvalues are non-negative by using `np.maximum(eigenvalues, 0)`.
            - Sorts the eigenvalues and corresponding eigenvectors in descending order.
        3. Singular Values Calculation:
            - Computes the singular values as the square roots of the eigenvalues of `AᵀA`.
            - Filters out any singular values close to zero (thresholded at `1e-10`).
        4. Matrix Construction:
            - Constructs the matrices `U`, `Σ`, and `Vᵀ` based on the eigenvalue decomposition.
        5. Error Handling:
            - Catches and raises appropriate exceptions for dimension mismatches, linear algebra issues, or any other unexpected errors during computation.


        Mathematical Background
        =======================

        Singular Value Decomposition (SVD) is a fundamental algorithm in linear algebra. It decomposes a given matrix A (of size m x n) into three components:
            A = U Σ V^T
        where:
        - U is an m x m orthogonal matrix, representing the left singular vectors of A.
        - Σ is an m x n diagonal matrix containing the singular values of A.
        - V is an n x n orthogonal matrix, and V^T contains the right singular vectors.

        This decomposition is used in many applications, including dimensionality reduction, pseudoinverse computation, and data compression.

        ---

        Problem and Approach
        --------------------

        The algorithm follows these steps:
        ----------------------------------

        1. Input Verification:
        Ensure the matrix A is 2D, as SVD is defined for matrices (not vectors or higher-dimensional tensors).

        2. Matrix Multiplications:
        Compute two related matrices:
        - A^T A (size n x n)—used to derive the right singular vectors V.
        - A A^T (size m x m)—used to derive the left singular vectors U.

        3. Eigenvalue Decomposition:
        Decompose A^T A and A A^T using the eigenvalue decomposition:
            A^T A = V Λ V^T,    A A^T = U Λ U^T
        Here:
        - Λ contains the eigenvalues of the respective matrices.
        - The columns of V and U are eigenvectors.

        4. Singular Values:
        The singular values are the square roots of the eigenvalues of A^T A (or equivalently A A^T):
            sigma_i = sqrt(λ_i)
        where λ_i are the eigenvalues of A^T A.

        5. Sorting:
        The eigenvalues are sorted in descending order, and the corresponding eigenvectors are rearranged accordingly.

        6. Normalizing U:
        The left singular vectors U are derived as:
            U = (A V) / sigma
        This ensures orthogonality while matching the relationship A = U Σ V^T.


        Mathematical Derivation of SVD
        ------------------------------

        1. Key Insight: Connection Between SVD and Eigenvalues
        The SVD is fundamentally related to the eigenvalue decomposition of A^T A and A A^T:
        - The eigenvalues of A^T A are the squares of the singular values sigma_i^2.
        - The eigenvectors of A^T A form the columns of V.
        - The eigenvectors of A A^T form the columns of U.

        2. Orthogonality
        The matrices U and V are orthogonal:
            U^T U = I    and    V^T V = I
        This ensures that the decomposition does not distort the input matrix.

        3. Reconstructing A
        Once U, Σ, and V are determined:
            A = U Σ V^T
        where Σ is diagonal and contains the singular values.


        Geometric Interpretation
        ------------------------

        1. Transformation of Basis:
        The matrix A can be seen as transforming an n-dimensional space into an m-dimensional space:
        - V: Defines a new orthonormal basis for the input space.
        - U: Defines a new orthonormal basis for the output space.
        - Σ: Scales and stretches the basis vectors.

        2. Rank of A:
        The rank of A is the number of non-zero singular values. If A has rank r, only r singular values are non-zero.

        3. Compression:
        The largest singular values correspond to the most significant contributions to A. Truncating small singular values yields a low-rank approximation.


        Logical Steps
        -------------

        Step 1: Compute A^T A and A A^T
        - A^T A: Captures the structure of the columns of A.
        - A A^T: Captures the structure of the rows of A.

        Step 2: Eigenvalue Decomposition
        - Compute the eigenvalues and eigenvectors of A^T A to get Λ (eigenvalues) and V (right singular vectors).
        - Compute the eigenvalues and eigenvectors of A A^T to get Λ (same eigenvalues) and U (left singular vectors).

        Step 3: Singular Values
        - Compute singular values as the square roots of the eigenvalues:
            sigma_i = sqrt(λ_i)

        Step 4: Normalization and Orthogonality
        - Normalize U using sigma to ensure orthogonality.

        Step 5: Truncation
        - Discard very small singular values (e.g., sigma < 10^-10) for numerical stability.



        Numerical Stability and Issues
        ------------------------------

        1. Ill-Conditioned Matrices:
        If A is near-singular or has very small singular values, the algorithm ensures numerical stability by truncating near-zero singular values.

        2. Efficiency:
        This method avoids explicitly forming Σ and uses eigenvalue decomposition, which is computationally efficient for dense or sparse matrices.

        3. Edge Cases:
        - If A is rank-deficient, some singular values will be zero.
        - If A is square and orthogonal, all singular values will be 1.


        Deep Mathematical Derivation of Singular Value Decomposition (SVD)
        ==================================================================

        To mathematically derive Singular Value Decomposition (SVD), we focus on breaking down a matrix A ∈ R^(m x n) into three fundamental components:
        A = U Σ V^T
        where:
        - U ∈ R^(m x m) is an orthogonal matrix (its columns are left singular vectors of A).
        - Σ ∈ R^(m x n) is a diagonal matrix containing the singular values (sigma_i).
        - V ∈ R^(n x n) is an orthogonal matrix (its columns are right singular vectors of A).


        Step 1: Understanding the Fundamental Problem
        ---------------------------------------------
        The goal of SVD is to decompose the matrix A in terms of its action on orthonormal bases. This involves:

        1. Finding Orthonormal Bases:
        We want two sets of orthonormal vectors:
        - U = [u_1, u_2, ..., u_m] for the range of A (spanning the row space and the null space).
        - V = [v_1, v_2, ..., v_n] for the domain of A.

        2. Singular Values:
        Singular values sigma_i are the scaling factors applied by A to the orthonormal basis v_i.


        Step 2: Connection to Eigenvalue Decomposition
        ----------------------------------------------

        1. Define A^T A and A A^T:
        - A^T A ∈ R^(n x n) is symmetric and positive semi-definite.
        - A A^T ∈ R^(m x m) is symmetric and positive semi-definite.

        2. The eigenvalue decomposition of A^T A:
        A^T A = V Λ V^T
        where:
        - Λ is a diagonal matrix containing the eigenvalues λ_i ≥ 0 of A^T A.
        - V is an orthogonal matrix whose columns are eigenvectors of A^T A.

        3. Similarly, the eigenvalue decomposition of A A^T:
        A A^T = U Λ U^T
        where:
        - Λ is a diagonal matrix containing the eigenvalues λ_i ≥ 0 of A A^T.
        - U is an orthogonal matrix whose columns are eigenvectors of A A^T.


        Step 3: Singular Values and Their Properties
        --------------------------------------------

        1. Relationship Between Eigenvalues and Singular Values:
        The eigenvalues of A^T A (and A A^T) are the squares of the singular values:
        λ_i = sigma_i^2  where  sigma_i ≥ 0.
        Singular values sigma_i = √λ_i are always non-negative.

        2. Nonzero Eigenvalues:
        Nonzero eigenvalues of A^T A and A A^T are the same. This happens because:
        rank(A^T A) = rank(A A^T) = rank(A).


        Step 4: Constructing U, Σ, and V
        --------------------------------

        1. Right Singular Vectors (V):
        The eigenvectors of A^T A form the columns of V. These eigenvectors span the input space of A.

        2. Left Singular Vectors (U):
        The eigenvectors of A A^T form the columns of U. These eigenvectors span the output space of A.

        3. Singular Values (Σ):
        Singular values sigma_i are the square roots of the eigenvalues of A^T A (or A A^T):
        sigma_i = √λ_i.
        The diagonal matrix Σ is constructed as:
        Σ = [ sigma_1  0  ...  0 ]
            [ 0    sigma_2  ...  0 ]
            [ ...  ...  ...  ... ]
            [ 0    0  ...  sigma_r ]
        where r = min(m, n).

        4. Normalization of U:
        U is normalized using:
        u_i = A v_i / sigma_i.
        This ensures that U is orthogonal.

        Step 5: Final Formulation

        1. Reconstruction of A:
        Using the components U, Σ, and V:
        A = U Σ V^T.

        2. Low-Rank Approximation:
        If k < r, a rank-k approximation of A can be written as:
        A_k = ∑(i=1 to k) sigma_i u_i v_i^T.
        This approximation retains the largest singular values, minimizing the reconstruction error.


        Deeper Insights: Geometry and Interpretation
        --------------------------------------------

        1. Action of A:
        The matrix A:
        - Rotates the input space (defined by V).
        - Scales along orthogonal directions (defined by singular values in Σ).
        - Rotates the output space (defined by U).

        2. Condition Number:
        The condition number of A is given by the ratio of the largest to smallest nonzero singular values:
        κ(A) = sigma_max / sigma_min.
        This measures the sensitivity of A to numerical instability.

        3. Rank of A:
        The rank of A equals the number of nonzero singular values.

        4. Energy Preservation:
        The Frobenius norm of A is related to its singular values:
        ||A||_F = √(∑(i=1 to r) sigma_i^2).
        Truncating smaller singular values preserves most of the matrix's "energy."

        5. Projection:
        The right singular vectors v_i represent directions of maximum variance, making SVD essential for Principal Component Analysis (PCA).



        Detailed Explanation: Connection to Eigenvalue Decomposition in Singular Value Decomposition (SVD)
        ==================================================================================================

        To understand the connection between SVD and eigenvalue decomposition, let's explore the mathematical foundations in greater detail.
        The goal is to explain why and how A^T A and A A^T relate to the singular value decomposition of a matrix A.

        Step 1: Eigenvalue Decomposition of A^T A and A A^T
        ---------------------------------------------------

        The Role of A^T A and A A^T
        1. Definition:
        - A^T A is a symmetric matrix of size n x n. It describes how the columns of A interact and forms a quadratic relationship.
        - A A^T is also symmetric but of size m x m. It describes how the rows of A interact.

        2. Properties of Symmetric Matrices:
        - Symmetric matrices are diagonalizable via orthogonal transformations.
        - The eigenvalues of symmetric matrices are always real.
        - Eigenvectors of symmetric matrices corresponding to distinct eigenvalues are orthogonal.


        Step 2: Eigenvalues of A^T A and A A^T are Related
        --------------------------------------------------

        Insight 1: Matrix Dimensions
        - A ∈ R^(m x n) implies:
        - A^T A ∈ R^(n x n): Square matrix of the input space of A.
        - A A^T ∈ R^(m x m): Square matrix of the output space of A.

        Insight 2: Shared Nonzero Eigenvalues
        - A^T A and A A^T have the same set of nonzero eigenvalues:
        - If λ is a nonzero eigenvalue of A^T A, it is also an eigenvalue of A A^T.
        - This arises because rank(A^T A) = rank(A A^T) = rank(A), and the rank corresponds to the number of nonzero eigenvalues.

        Proof of Shared Eigenvalues:
        1. Consider x ≠ 0, an eigenvector of A^T A with eigenvalue λ:
        A^T A x = λ x.
        2. Multiply both sides by A:
        A A^T (A x) = λ (A x).
        Here, A x ≠ 0 (otherwise, x = 0), so A x is an eigenvector of A A^T with eigenvalue λ.

        This symmetry in eigenvalues underpins the connection between the eigenvalue decomposition of A^T A, A A^T, and the SVD of A.


        Step 3: Eigenvectors of A^T A and A A^T
        ---------------------------------------

        Right Singular Vectors from A^T A:
        - The eigenvectors of A^T A form the columns of V in SVD.
        - To see why, let v_i be an eigenvector of A^T A:
        A^T A v_i = λ_i v_i.
        - In the SVD context, v_i is a right singular vector of A, and the eigenvalue λ_i = sigma_i^2 gives the corresponding singular value sigma_i.

        Left Singular Vectors from A A^T:
        - The eigenvectors of A A^T form the columns of U in SVD.
        - Let u_i = A v_i / sigma_i. Then:
        A A^T u_i = A (A^T A v_i / sigma_i) = sigma_i^2 u_i.
        - Thus, u_i is an eigenvector of A A^T, and sigma_i is its singular value.


        Step 4: Relating SVD to Eigenvalue Decomposition
        ------------------------------------------------

        Now, let us see how A = U Σ V^T emerges naturally:

        1. SVD Representation:
        - In SVD, we aim to decompose A such that:
            A = U Σ V^T,
            where U and V are orthogonal matrices, and Σ is diagonal.

        2. Matrix Products:
        - A^T A = (U Σ V^T)^T (U Σ V^T) = V Σ^T Σ V^T.
            - Here, V^T V = I, so A^T A = V Σ^T Σ V^T.
            - This matches the eigenvalue decomposition of A^T A, with V as the eigenvectors and Σ^T Σ = diag(sigma_1^2, ..., sigma_r^2).

        - Similarly:
            A A^T = (U Σ V^T)(U Σ V^T)^T = U Σ Σ^T U^T.
            - Here, U^T U = I, so A A^T = U Σ Σ^T U^T.
            - This matches the eigenvalue decomposition of A A^T, with U as the eigenvectors and Σ Σ^T = diag(sigma_1^2, ..., sigma_r^2).

        3. Singular Values:
        - The eigenvalues of A^T A and A A^T are the squares of the singular values:
            sigma_i^2 = λ_i.


        Step 5: Geometric Interpretation
        --------------------------------

        The matrices A^T A and A A^T project the matrix A into its domain (R^n) and range (R^m), respectively:

        1. Action of A^T A:
        - Acts on the domain of A (column space).
        - Eigenvectors v_i of A^T A define the directions in the domain where A scales by sigma_i^2.

        2. Action of A A^T:
        - Acts on the range of A (row space).
        - Eigenvectors u_i of A A^T define the directions in the range where A scales by sigma_i^2.


        Summary of Connection
        ---------------------

        The connection between eigenvalue decomposition and SVD is as follows:
        1. A^T A reveals the right singular vectors (V) and the squared singular values (sigma_i^2).
        2. A A^T reveals the left singular vectors (U) and the squared singular values (sigma_i^2).
        3. These eigenvalue decompositions are symmetric projections of A, from which A = U Σ V^T emerges naturally.
        """).strip()

            mbsag_solver=textwrap.dedent("""
        This method implements the Mini-Batch Stochastic Average Gradient (MBSAG) solver,which is used for optimizing model parameters in supervised learning tasks like regression and classification.
        The method updates weights and biases iteratively using mini-batches of data and tracks gradients for efficient updates, reducing the variance of stochastic gradient descent (SGD).

        Parameters:
        -----------
        - X: np.ndarray
            Feature matrix of shape (m, n), where `m` is the number of samples, and `n` is the number of features.
        - y: np.ndarray
            Target vector or matrix of shape (m,) or (m, k), where `k` is the number of target variables.

        Returns:
        --------
        None

        Raises:
        -------
        - RuntimeError: If any unexpected error occurs during the computation, such as gradient calculation or data shuffling errors.

        Theoretical Explanation
        ========================

        The Mini-Batch Stochastic Average Gradient (MBSAG) algorithm improves upon traditional stochastic gradient descent by maintaining a memory of previous gradients for each sample. This memory enables more accurate updates and faster convergence, especially for large datasets.

        Core Components:
        1. Gradient Memory:
        - Tracks the gradient for each sample, allowing efficient updates by calculating the difference between the current and previous gradients.

        2. Mini-Batch Updates:
        - The method processes data in small batches, reducing memory requirements and improving computational efficiency.

        3. Weight and Bias Updates:
        - Uses the average gradient from mini-batches to iteratively update the model's weights and bias. The bias is updated separately if `self.fit_intercept` is True.

        4. Early Stopping:
        - Monitors validation loss over epochs and stops training if the loss does not improve for a specified number of iterations (`self.patience`).


        Algorithm Workflow
        ==================

        1. Initialization:
        - If `self.max_iter` is not provided, it is set dynamically based on the dataset size.
        - Initializes weights, bias, gradient memory, and related parameters.

        2. Data Shuffling:
        - Randomly shuffles the data at the beginning of each epoch to improve generalization and avoid biases in gradient computation.

        3. Mini-Batch Processing:
        - Splits the dataset into mini-batches of size `self.batch_size`.
        - For each mini-batch:
            - Predicts the target values (`y_pred`) using the current model.
            - Computes gradients for weights and biases using the loss function.
            - Updates weights and gradient memory using the average gradient across the mini-batch.

        4. Loss and Metrics:
        - Tracks loss, Mean Absolute Error (MAE), Mean Squared Error (MSE), Root Mean Squared Error (RMSE), and R² score for each epoch.
        - Logs these metrics if `self.verbose` is True.

        5. Early Stopping:
        - Monitors validation loss and stops training if the improvement is below a specified threshold (`self.tol`) for `self.patience` epochs.

        Method Details
        ==============

        1. Gradient Computation:
        - Gradients are calculated using a loss function (e.g., Mean Squared Error) and stored in the `gradient_memory`.

        2. Weight Updates:
        - The model weights are updated using the average gradient, scaled by the learning rate (`self.alpha`).

        3. Bias Updates:
        - If `self.fit_intercept` is True, the bias is updated using the mean error across the mini-batch.

        4. Performance Metrics:
        - Computes additional metrics such as R² score and RMSE to evaluate model performance at each epoch.

        5. History Logging:
        - Stores the weights and bias at each epoch for analysis or rollback purposes.

        Example Verbose Output:
        ------------------------
        Epoch 5/100 - 10/10 [=========================] - 3.5s 0.35ms/step - loss: 0.0345 - mae: 0.0256 - mse: 0.0012 - rmse: 0.0346 - r2_score: 0.9123 - val_loss: 0.0412


        More Explanation
        ================
        This method is to implement a Modified Mini-batch Stochastic Average Gradient (MBSAG) algorithm
        for solving optimization problems in machine learning, typically for training linear models like logistic regression or
        linear regression. Below is a detailed breakdown of the mathematical and logical workings of the function:


        Key Concepts of the Algorithm
        =============================

        1. Gradient Descent:
        - This algorithm optimizes the weights (w) and bias (b) of a machine learning model by minimizing a loss function, such as
            Mean Squared Error (MSE) or cross-entropy loss.
        - The gradient of the loss function with respect to w and b is computed, which tells us the direction in which to adjust the
            parameters to reduce the loss.

        2. Stochastic Optimization:
        - Instead of computing the gradient on the entire dataset (as in batch gradient descent), the function operates on small
            mini-batches of the dataset to make updates faster and computationally efficient.

        3. Average Gradient (SAG):
        - Unlike regular stochastic gradient descent (SGD), SAG keeps track of all previously computed gradients in memory and
            updates the model weights using the average of the gradients. This helps smooth updates and improves convergence stability.

        4. Early Stopping:
        - The algorithm halts training if no improvement is observed in the validation loss after a certain number of iterations
            (patience). This prevents overfitting and saves computation time.


        Mathematical Background
        =======================

        Initialization
        --------------
        1. X ∈ R^(m x n): The dataset of m samples, each with n features.
        2. y ∈ R^m: The target variable corresponding to X. For multiple outputs, y ∈ R^(m x k), where k is the number of target
        dimensions.
        3. Parameters:
        - w ∈ R^n: The weight vector initialized randomly or to zeros.
        - b ∈ R: The bias term initialized to zero (if `fit_intercept` is true).

        Gradient Computation
        --------------------
        - For a single sample (X_i, y_i):
        - y_pred = f(X_i; w, b): The predicted output using the current weights and bias. f can be linear (X_i^T w + b) or non-linear
            (logistic/sigmoid).
        - Loss Function (L):
            - Example for MSE: L(w, b) = (1/m) Σ_(i=1)^m (y_i - y_pred)^2.
            - Gradient of Loss with respect to w:
            ∇_w L(w, b) = -(1/m) Σ_(i=1)^m X_i^T (y_i - y_pred)
            - Gradient with respect to b:
            ∇_b L(w, b) = -(1/m) Σ_(i=1)^m (y_i - y_pred)

        Updating Weights Using MBSAG
        ----------------------------
        - Gradient Memory (G):
        - The algorithm maintains a memory of gradients for all samples, G ∈ R^(m x n).
        - Initially, G = 0 for all samples.
        - Average Gradient (Ḡ):
        - The average gradient is updated incrementally:
            Ḡ = Ḡ + (1/m) (∇_w^new - G_prev)
            - Here, ∇_w^new is the gradient for the current mini-batch, and G_prev is the previous gradient stored in memory.
            - The memory G is updated with the new gradient.
        - Weight Update Rule:
        - Using a learning rate  alpha :
            w = w -  alpha  Ḡ
        - For the bias:
            b = b -  alpha  g_b̄
            where g_b̄ is the average gradient for the bias.

        Batch Processing
        ----------------
        - The dataset is shuffled randomly at the start of each epoch to avoid correlation patterns affecting training.
        - Mini-batches of size batch_size are processed iteratively, and updates are made for each batch.

        Loss and Metrics Monitoring
        ---------------------------
        1. Epoch Loss:
        - The cumulative loss for all batches in an epoch is computed and divided by the total number of samples:
            epoch_loss = (1/m) Σ_(i=1)^m L(w, b)
        2. Performance Metrics:
        - Mean Absolute Error (MAE):
            MAE = (1/m) Σ_(i=1)^m |y_i - y_pred|
        - Root Mean Squared Error (RMSE):
            RMSE = √((1/m) Σ_(i=1)^m (y_i - y_pred)^2)
        - R² Score:
            R² = 1 - ((Σ_(i=1)^m (y_i - y_pred)^2) / (Σ_(i=1)^m (y_i - ȳ)^2))

        Early Stopping
        --------------
        - If the validation loss does not improve by a tolerance (tol) for patience consecutive epochs, training stops:
        patience_counter =
        {
            0 if val_loss < best_loss - tol
            patience_counter + 1 otherwise
        }


        Logical Flow
        ============
        1. Initialize Parameters:
        - Initialize weights, bias, gradient memory, and hyperparameters.

        2. Iterative Training:
        - Shuffle the data at the start of each epoch.
        - Process data in mini-batches, compute gradients, and update weights and bias.

        3. Monitor Metrics:
        - Compute loss and metrics after each epoch.
        - Check for early stopping based on validation loss.

        4. Output:
        - Return the optimized weights and bias, along with training history.


        Gradient Computation: Explanation
        =================================
        Gradient computation is the core of optimization in machine learning models.
        It involves finding the direction and magnitude by which the model's parameters (weights and bias) should be adjusted to minimize a loss function.

        Predictions
        -----------
        For a dataset X ∈ R^(m x n) with m samples and n features, the predicted output y_pred is calculated as:
        y_pred = Xw + b
        where:
        - w ∈ R^n: weight vector.
        - b ∈ R: bias term.
        - y_pred ∈ R^m: predictions for all samples.

        If y_pred is passed through an activation function (e.g., sigmoid for classification), it becomes:
        y_pred = sigma(Xw + b), where sigma(z) = 1 / (1 + e^(-z))

        Loss Function
        -------------
        The loss function quantifies how far the predicted values y_pred are from the actual values y. Some common loss functions are:

        Mean Squared Error (MSE):
        L(w, b) = (1/m) ∑(i=1 to m) (y_i - y_pred,i)^2

        Binary Cross-Entropy (for classification):
        L(w, b) = -(1/m) ∑(i=1 to m) [ y_i log(y_pred,i) + (1 - y_i) log(1 - y_pred,i) ]

        Gradients of the Loss Function
        ------------------------------
        The goal is to compute the gradient of L(w, b) with respect to the weights w and the bias b.
        Gradients represent the slope or rate of change of the loss function with respect to these parameters.

        Gradient with Respect to w:
        The gradient of the loss function L with respect to w is given by:
        ∇w L(w, b) = ∂L / ∂w

        For MSE, substituting the loss:
        ∇w L(w, b) = -(1/m) ∑(i=1 to m) X_i^T (y_i - y_pred,i)
        where:
        - X_i ∈ R^n: feature vector of sample i.
        - y_i - y_pred,i: residual error for sample i.

        For binary cross-entropy:
        ∇w L(w, b) = -(1/m) ∑(i=1 to m) X_i^T (y_i - y_pred,i)
        The structure is similar to MSE because the derivative of the sigmoid activation is embedded in the residual y_i - y_pred,i.

        Gradient with Respect to b:
        The gradient of L with respect to b is given by:
        ∇b L(w, b) = ∂L / ∂b

        For MSE:
        ∇b L(w, b) = -(1/m) ∑(i=1 to m) (y_i - y_pred,i)

        For binary cross-entropy:
        ∇b L(w, b) = -(1/m) ∑(i=1 to m) (y_i - y_pred,i)

        Mini-Batch Gradient Computation
        -------------------------------
        Instead of computing the gradient over the entire dataset, we compute it for a mini-batch of size batch_size.
        For a mini-batch {(X_j, y_j)} with indices j ranging from 1 to batch_size, the gradients are:

        - For w:
        ∇w L(w, b) = -(1/batch_size) ∑(j=1 to batch_size) X_j^T (y_j - y_pred,j)

        - For b:
        ∇b L(w, b) = -(1/batch_size) ∑(j=1 to batch_size) (y_j - y_pred,j)

        Gradient Averaging (in SAG)
        ---------------------------
        To smooth updates and incorporate information from past gradients, the algorithm maintains a gradient memory G for all samples and updates the average gradient G_bar using:
        G_bar = G_bar + (1/m) (∇w^new - G_prev)
        Here:
        - ∇w^new: Gradient of the current mini-batch.
        - G_prev: Previously stored gradient for the samples in the mini-batch.

        This averaging stabilizes the weight updates and ensures smoother convergence.

        Weight and Bias Updates
        -----------------------
        After computing the gradients, the weights w and bias b are updated using the learning rate  alpha :
        - For w:
        w = w -  alpha  G_bar
        - For b:
        b = b -  alpha  g_b_bar
        where g_b_bar is the averaged gradient for the bias.


        The derivation of the loss function: Explanation
        ================================================

        1. Derivation for Linear Regression with Mean Squared Error (MSE) as the loss function.
        2. Sow it is used to compute the gradients with respect to the model parameters (weights and bias).


        Linear Regression Model
        -----------------------
        In linear regression, the goal is to find the weights w and bias b that minimize the error between the true values y and the predicted values y_pred.

        The predicted output for a given input X (where X in R^(m x n) is a matrix of m samples and n features) is computed as:

        y_pred = Xw + b

        where:
        - w in R^n is the weight vector.
        - b in R is the bias term.
        - Xw is the linear transformation of the input data.
        - y_pred in R^m is the vector of predictions.

        Mean Squared Error (MSE) Loss Function
        --------------------------------------
        The MSE loss function measures the average squared difference between the predicted and actual values. It is given by:

        L(w, b) = (1/m) sum(i=1 to m) (y_i - y_pred_i)^2

        where:
        - y_i is the true value of the i-th sample.
        - y_pred_i = X_i w + b is the predicted value for the i-th sample.
        - m is the number of samples in the dataset.

        The goal is to minimize this loss function, i.e., find w and b that result in the smallest error between the predicted and actual values.


        Derivation of Gradients
        -----------------------
        To minimize the loss function, we need to compute the gradients of the loss function with respect to the parameters w and b.
        These gradients will tell us how to update w and b in the right direction to minimize the loss.

        Gradient with Respect to Weights (w)
        ------------------------------------
        To find the gradient of the loss function with respect to the weights w, we compute the partial derivative of L(w, b) with respect to w.

        1. First, expand the MSE loss function:

        L(w, b) = (1/m) sum(i=1 to m) (y_i - (X_i w + b))^2

        where X_i is the feature vector of the i-th sample.

        2. Now, apply the chain rule to compute the derivative of the loss function with respect to w:

        dL(w, b) / dw = (1/m) sum(i=1 to m) d/dw (y_i - (X_i w + b))^2

        3. The derivative of (y_i - (X_i w + b))^2 with respect to w is:

        d/dw (y_i - (X_i w + b))^2 = -2 X_i^T (y_i - (X_i w + b))

        So the gradient of the MSE loss with respect to w is:

        grad_w L(w, b) = -(2/m) sum(i=1 to m) X_i^T (y_i - (X_i w + b))

        This tells us how to adjust the weights w to minimize the error.


        Gradient with Respect to Bias (b)
        ---------------------------------
        Next, we compute the gradient of the loss function with respect to the bias b. Using the same approach, we compute the partial derivative of L(w, b) with respect to b.

        1. The partial derivative of the MSE loss function with respect to b is:

        dL(w, b) / db = (1/m) sum(i=1 to m) d/db (y_i - (X_i w + b))^2

        2. The derivative of (y_i - (X_i w + b))^2 with respect to b is:

        d/db (y_i - (X_i w + b))^2 = -2 (y_i - (X_i w + b))

        So the gradient of the MSE loss with respect to b is:

        grad_b L(w, b) = -(2/m) sum(i=1 to m) (y_i - (X_i w + b))


        Gradient Descent Update Rule
        ----------------------------
        Once the gradients are computed, we can update the parameters using the gradient descent update rule. This rule moves the parameters in the opposite direction of the gradient to reduce the loss.

        1. For weights w:

        w <- w - alpha grad_w L(w, b)

        where alpha is the learning rate.

        2. For bias b:

        b <- b - alpha grad_b L(w, b)

        """).strip()

            compute_r2_score =textwrap.dedent("""
        This method computes the R² (R-squared) score, a statistical measure of the proportion of the variance in the dependent variable
        that is predictable from the independent variables. It provides an indication of how well the model's predictions match the true data.

        Parameters:
        -----------
        - y_true: numpy.ndarray
            A 1D array containing the actual values (true values) of the dependent variable.

        - y_pred: numpy.ndarray
            A 1D array containing the predicted values from the model for the dependent variable.

        Returns:
        --------
        - r2_score: float
            The R² score, a number between 0 and 1, where 1 indicates perfect prediction and 0 indicates that the model does not explain
            any variance in the dependent variable. A negative value can occur if the model performs worse than a horizontal line (mean of y_true).

        Raises:
        -------
        - ValueError: If `y_true` and `y_pred` do not have the same length.
        - TypeError: If either `y_true` or `y_pred` is not a numpy ndarray or is an incompatible type.
        - Exception: If any unexpected error occurs during computation.

        Method Details
        ==============
        The R² score is calculated as:
            R² = 1 - (residual_variance / total_variance)

        Where:
        - total_variance = Σ(y_true - mean(y_true))²: The total variance in the true data, representing how much the actual values deviate
        from their mean.
        - residual_variance = Σ(y_true - y_pred)²: The residual variance, representing how much the predicted values deviate from the true values.

        The R² score ranges from 0 to 1:
        - A score of 1 means the model perfectly predicts the true values.
        - A score of 0 means the model does no better than predicting the mean of the actual values.
        - A negative score indicates that the model is worse than predicting the mean.
        """).strip()

            compute_gradients = textwrap.dedent("""
        This method computes the gradients of the loss function with respect to the model parameters (weights and bias)
        for a linear regression model using the Mean Squared Error (MSE) loss function. The gradients are used for optimization
        in gradient descent or other optimization algorithms.

        Parameters:
        -----------
        - X: numpy.ndarray
            A 2D array of shape (n_samples, n_features) representing the input data, where `n_samples` is the number of training
            samples and `n_features` is the number of features (independent variables).

        - y: numpy.ndarray
            A 1D or 2D array of shape (n_samples,) or (n_samples, n_outputs) representing the true target values for the regression task.

        - y_pred: numpy.ndarray
            A 1D or 2D array of shape (n_samples,) or (n_samples, n_outputs) representing the predicted values for the target variable
            based on the current model parameters.

        Returns:
        --------
        - gradients: dict
            A dictionary containing the gradients with respect to the model's parameters:
            - 'weights': The gradient of the loss function with respect to the weights (of shape (n_features,)).
            - 'bias' (optional): The gradient of the loss function with respect to the bias (a scalar), included if `fit_intercept` is True.

        Raises:
        -------
        - Exception: If an unexpected error occurs during the computation of the gradients.

        Method Details
        ==============
        This method computes the gradients as follows:

        1. Gradient with respect to the weights (gradients_w):
            - The gradient with respect to the weights is calculated using the formula:
                gradients_w = (Xᵀ @ (y_pred - y)) / n_samples
            Where:
                - Xᵀ is the transpose of the input matrix X.
                - (y_pred - y) is the residual error (predicted values minus true values).
                - n_samples is the number of samples in the dataset (X.shape[0]).

        2. Gradient with respect to the bias (gradients_b):
            - If the `fit_intercept` flag is set to True, the gradient with respect to the bias is calculated as the mean of the residuals:
                gradients_b = np.mean(y_pred - y, axis=0)

        3. Return Value:
            - A dictionary containing the computed gradients:
                - 'weights' key holds the gradient with respect to the weights.
                - If `fit_intercept` is True, the 'bias' key holds the gradient with respect to the bias term.

        """).strip()

            compute_loss = textwrap.dedent("""
        This method computes the loss function for the model, which quantifies the difference between the true target values and the
        predicted values from the model. In this case, it uses the Mean Squared Error (MSE) as the loss function, which is commonly
        used in regression tasks to measure the model's performance.

        Parameters:
        -----------
        - X: numpy.ndarray
            A 2D array of shape (n_samples, n_features) representing the input data, where `n_samples` is the number of training samples
            and `n_features` is the number of features (independent variables).

        - y: numpy.ndarray
            A 1D or 2D array of shape (n_samples,) or (n_samples, n_outputs) representing the true target values for the regression task.

        Returns:
        --------
        - loss: float
            The computed loss value, which is the mean of the sum of squared differences between the predicted values and the true values
            for each sample. A lower loss indicates a better fit of the model to the data.

        Raises:
        -------
        - Exception: If an unexpected error occurs during the computation of the loss.

        Method Details
        ==============
        This method computes the loss as follows:

        1. Prediction:
            - The method first generates predictions using the `predict` method of the model, based on the input data `X`.

        2. Loss Calculation:
            - The loss is computed using the Mean Squared Error (MSE) formula:
                loss = np.mean(np.sum((y - predictions) ** 2, axis=1))
            Where:
                - (y - predictions) is the residual error (the difference between the true values and predicted values).
                - (y - predictions) ** 2 represents the squared residuals.
                - np.sum(..., axis=1) sums the squared residuals for each sample across all features (if applicable).
                - np.mean(...) computes the average of these summed squared residuals across all samples.

        3. Return Value:
            - The computed loss value is returned, which indicates the overall performance of the model on the given data.

        """).strip()

            cholesky_solver = textwrap.dedent("""
        This method implements a Cholesky decomposition-based solver for Ridge Regression,
        a linear regression model with L2 regularization. It computes the model's weights and biases,
        supporting handling of intercepts and multivariate outputs.

        Parameters:
        -----------
        - X: numpy.ndarray
            Input feature matrix of shape (m, n), where `m` is the number of samples
            and `n` is the number of features.
        - y: numpy.ndarray
            Target values of shape (m, 1) for single output or (m, k) for multiple outputs.

        Returns:
        --------
        - Updates the instance with the computed weights (`self.weights`) and biases (`self.bias`).

        Raises:
        -------
        - ValueError: If `X` and `y` contain NaN or infinite values, or if `alpha` is non-positive.
        - ZeroDivisionError: If a zero is encountered on the diagonal during decomposition.
        - RuntimeError: If any unexpected issue occurs during computation.

        Theoretical Explanation
        =======================

        Cholesky Decomposition
        -----------------------
        Cholesky decomposition is used to solve systems of linear equations for positive definite matrices.
        It decomposes a symmetric, positive definite matrix `A` into the product of a lower triangular matrix
        `L` and its transpose:
            A = LLᵀ

        Ridge Regression Formulation
        ----------------------------
        Ridge Regression minimizes the following regularized objective function:
            min_w ||y - Xw||² +  alpha ||w||²
        where:
        - ` alpha ` is the regularization parameter controlling the L2 penalty term.

        The normal equation for Ridge Regression becomes:
            (XᵀX +  alpha I)w = Xᵀy
        where:
        - `I` is the identity matrix.
        - `XᵀX +  alpha I` is guaranteed to be symmetric and positive definite for ` alpha  > 0`.

        By applying Cholesky decomposition:
            (XᵀX +  alpha I) = LLᵀ
        The solution for `w` is obtained by solving two triangular systems:
            1. Solve Lz = Xᵀy for `z`.
            2. Solve Lᵀw = z for `w`.

        Multivariate Outputs
        --------------------
        For multiple outputs (`y` with multiple columns), the solution generalizes to compute weights for
        each output column independently.

        Method Details
        ==============
        1. Input Validation:
           - Ensures that `X` and `y` are finite and that `alpha` is positive.
        2. Data Centering:
           - Centers `X` and `y` around their means if `fit_intercept` is enabled.
        3. Matrix Construction:
           - Constructs the regularized normal equation matrix: `A = XᵀX +  alpha I`.
        4. Cholesky Decomposition:
           - Computes the lower triangular matrix `L` through iterative decomposition.
           - Handles errors such as non-positive definiteness or zero diagonal elements.
        5. Solving:
           - Solves the triangular systems to compute weights.
        6. Bias Calculation:
           - Computes the intercept term if `fit_intercept` is enabled.

        Edge Cases and Error Handling
        =============================
        - Handles cases where `X` or `y` contain NaN or infinite values.
        - Validates that the regularization parameter `alpha` is positive.
        - Detects and raises errors for matrices that are not positive definite.

        Computational Complexity
        ========================
        - Cholesky decomposition is efficient with complexity O(n³) for `n` features.


        Cholesky Decomposition:
        =======================

        This documentation provides an explanation of solving linear systems using Cholesky Decomposition, particularly in the context of Ridge Regression.

        Problem Setup
        =============
        We aim to solve the Ridge Regression equation:
            A w = b
        Where:
        - A = X.T @ X + alpha * I: Symmetric and positive definite matrix.
        - b = X.T @ y: Vector (or matrix for multiple outputs) derived from the input features X and targets y.
        - w: The weight vector to solve for.

        Cholesky Decomposition breaks A into:
            A = L @ L.T
        Where:
        - L: A lower triangular matrix (all elements above the diagonal are zero).
        - L.T: The transpose of L, an upper triangular matrix.


        Why Cholesky Works
        ==================
        For a symmetric positive definite matrix A:
        - Symmetry ensures A[i, j] = A[j, i], meaning the decomposition A = L @ L.T is possible.
        - Positive definiteness ensures all eigenvalues of A are positive, so L[i, i] > 0 during decomposition (avoiding division by zero or negative square roots).

        By decomposing A into L @ L.T, we reduce the original problem into two simpler systems of equations, solved in two stages.


        Step-by-Step Process
        ====================

        Step 1: Decompose A into L @ L.T
        ---------------------------------
        We iteratively compute the elements of L using the formula:
        - For diagonal elements L[i, i]:
            L[i, i] = sqrt(A[i, i] - sum(L[i, k]**2 for k in range(i)))
        This ensures that the diagonal elements of L are positive.

        - For off-diagonal elements L[i, j] (j < i):
            L[i, j] = (A[i, j] - sum(L[i, k] * L[j, k] for k in range(j))) / L[j, j]

        This step is done row by row (or column by column), ensuring that only previously computed elements of L are used.

        Step 2: Solve Lz = b
        ---------------------
        Once A = L @ L.T is computed, substitute it into the original equation:
            A w = b  ->  L @ L.T @ w = b

        First, solve for an intermediate vector z:
            Lz = b
        This is done using forward substitution:
        - For each z[i]:
            z[i] = (b[i] - sum(L[i, k] * z[k] for k in range(i))) / L[i, i]

        Since L is lower triangular, each z[i] depends only on previously computed z[k], making it computationally efficient.

        Step 3: Solve L.T @ w = z
        --------------------------
        Finally, solve for w:
            L.T @ w = z
        This is done using backward substitution:
        - For each w[i] (starting from the last row and working upwards):
            w[i] = (z[i] - sum(L[k, i] * w[k] for k in range(i + 1, n))) / L[i, i]

        Since L.T is upper triangular, this step proceeds in reverse order.


        Mathematical Flow
        =================
        Here's the flow of computations in a compact form:

        1. Decomposition:
            Compute L row by row:
            L[i, i] = sqrt(A[i, i] - sum(L[i, k]**2 for k in range(i)))
            L[i, j] = (A[i, j] - sum(L[i, k] * L[j, k] for k in range(j))) / L[j, j], for j < i

        2. Forward Substitution:
            Solve Lz = b:
            z[i] = (b[i] - sum(L[i, k] * z[k] for k in range(i))) / L[i, i]

        3. Backward Substitution:
            Solve L.T @ w = z:
            w[i] = (z[i] - sum(L[k, i] * w[k] for k in range(i + 1, n))) / L[i, i]


        Computational Insights
        ======================
        1. Efficiency:
        - Cholesky decomposition is efficient for dense matrices, with complexity O(n^3) for n-dimensional matrices.
        - Solving triangular systems (forward/backward substitution) takes O(n^2).

        2. Numerical Stability:
        - Adding alpha * I to X.T @ X ensures positive definiteness, improving numerical stability.
        - Unlike direct inversion (A**-1 @ b), Cholesky avoids numerical instability caused by inverting poorly conditioned matrices.

        3. Scalability:
        - While suitable for moderate-sized problems (n <= 10,000), it becomes computationally expensive for very large feature spaces.


        Ridge Regression with Cholesky
        ==============================
        The Cholesky method handles the regularization naturally by incorporating alpha * I into A.
        It avoids overfitting by shrinking the weights w, especially when features are correlated or when n > m (more features than samples).

        By using L @ L.T, the solution to Ridge Regression is computed efficiently, leveraging the properties of triangular matrices for computational speed and numerical stability.


        Method Breakdown:
        =================

        The Cholesky solver is designed to solve Ridge Regression problems using Cholesky Decomposition.
        Below is a detailed mathematical and logical explanation of how it works.

        Ridge Regression Overview
        -------------------------
        Ridge Regression is a linear regression method with an L2 regularization term to penalize
        large coefficients, helping prevent overfitting. It minimizes the following cost function:

            min_w ||y - Xw||^2 + alpha ||w||^2

        Here:
        - X is the input feature matrix (m x n), with m samples and n features.
        - y is the target vector (m x 1) or (m x k) for multivariate outputs.
        - w is the weight vector (n x 1).
        - alpha > 0 is the regularization parameter, controlling the trade-off between fit and regularization.

        This can be rewritten as the Ridge Regression normal equation:

            (X^T X + alpha I)w = X^T y

        - X^T X is the Gram matrix (n x n), summarizing the relationships between features.
        - I is the identity matrix (n x n), scaled by alpha for regularization.

        Solving Using Cholesky Decomposition
        ------------------------------------
        The key mathematical idea here is solving the normal equation (X^T X + alpha I)w = X^T y
        using Cholesky Decomposition. This is because the matrix X^T X + alpha I is symmetric and
        positive definite (when alpha > 0), which makes it suitable for Cholesky.

        Step-by-Step Breakdown
        ----------------------
        1. Form the Matrix A:
            A = X^T X + alpha I
            - X^T X: Captures the relationships between features.
            - alpha I: Adds a diagonal penalty to ensure A is invertible and well-conditioned
                        (numerically stable).

        2. Cholesky Decomposition of A:
            Decompose A into the product of a lower triangular matrix L and its transpose L^T:
                A = L L^T
            This breaks the problem into simpler parts because L is triangular.

        3. Solve Lz = X^T y for z:
            Use forward substitution (since L is lower triangular):
                z = L^(-1) (X^T y)

        4. Solve L^T w = z for w:
            Use backward substitution (since L^T is upper triangular):
                w = (L^T)^(-1) z

            Together, these steps solve (X^T X + alpha I)w = X^T y efficiently without directly
            inverting A, which can be computationally expensive.

        Handling Intercept (Bias Term)
        ------------------------------
        If fit_intercept is enabled, the inputs X and y are centered to isolate the effect of
        features from the bias term.

        1. Center X:
            Subtract the mean of each column:
                X <- X - mean(X, axis=0)

        2. Center y:
            Subtract the mean of y:
                y <- y - mean(y)

        After solving for w, the bias b is calculated as:
            b = mean(y) - mean(X)^T w
        This ensures that the intercept term captures the global offset of the data.

        Regularization Effect
        ---------------------
        The term alpha I in the matrix A prevents the problem from becoming ill-posed
        (e.g., when features are highly correlated or X^T X is near-singular). Mathematically:
        - alpha I adds a small penalty to each diagonal element of X^T X, making the eigenvalues
            of A strictly positive.
        - This ensures numerical stability and reduces overfitting by shrinking the coefficients w.

        Error Handling and Matrix Properties
        ------------------------------------
        The method includes robust checks to ensure the decomposition works:
        - Positive Definiteness: During decomposition, the diagonal elements of L (L[i, i])
            must remain positive. If not, A is not positive definite, and decomposition fails.
        - Zero Division Check: Diagonal elements (L[i, i]) are checked for zero values, as this
            would make subsequent calculations invalid.

        Mathematically, these checks ensure:
        - The matrix A has valid properties for Cholesky decomposition.
        - Errors are raised if the assumptions (e.g., alpha > 0) are violated.

        Computational Complexity
        ------------------------
        - Matrix Multiplications: Forming X^T X and X^T y takes O(m n^2), where m is the number
            of samples and n is the number of features.
        - Cholesky Decomposition: Decomposing A (size n x n) takes O(n^3).
        - Forward/Backward Substitution: Solving Lz = X^T y and L^T w = z takes O(n^2).

        Overall complexity is dominated by the O(n^3) decomposition step, making this method
        suitable for moderate feature dimensions (n).

        Logical Steps
        -------------
        - Input Validation: Ensure X, y, and alpha are valid.
        - Preprocessing: Center X and y if needed.
        - Matrix Construction: Compute X^T X + alpha I and X^T y.
        - Cholesky Decomposition: Decompose A into LL^T.
        - Solving: Use forward and backward substitution to compute w.
        - Bias Calculation: Compute b if intercept is included.


        Logical Workflow:
        =================

        Step 1: Input Validation
        ------------------------
        This step ensures that the input data and parameters are suitable for computation. The solver performs the following checks:

        1. Convert Inputs to Arrays:
        Ensure that both X (features) and y (targets) are converted into NumPy arrays. This makes them compatible with matrix operations.

        - Reason: Inputs might be in different formats (e.g., lists or pandas DataFrames). NumPy ensures consistency for subsequent calculations.

        2. Check for Invalid Values:
        Verify that X and y do not contain NaN or Infinity. These values can corrupt calculations like matrix multiplication or decomposition.

        - Example: If any element of X or y is non-finite, the matrix XT X or XT y will also be invalid.

        3. Validate Regularization Parameter (alpha):
        Confirm that alpha > 0. The regularization parameter controls the L2 penalty and ensures XT X + alpha I is positive definite.

        - Why it matters: If alpha <= 0, the regularization term vanishes or becomes invalid, possibly leading to numerical instability.

        Step 2: Preprocessing
        ---------------------
        If fit_intercept is enabled, the input data (X and y) are centered by subtracting their means.

        1. Center X:
        Compute the mean of each column of X (feature-wise means) and subtract it from each corresponding feature.
        This ensures that the model does not misinterpret offsets in the data as meaningful relationships.

        - Formula:
            X <- X - mean(X, axis=0)
        - Mathematical reasoning: Centering ensures the learned weights w are independent of feature means, allowing the bias b to account for any global offsets.

        2. Center y:
        Compute the mean of y and subtract it, making y zero-centered.

        - Formula:
            y <- y - mean(y)
        - Why: Centering y ensures that the intercept b captures the average target value when all features are at their mean.

        3. Skip Centering if fit_intercept=False:
        If intercept handling is disabled, the solver directly works with raw X and y.

        Step 3: Matrix Construction
        ---------------------------
        This step prepares the matrices required for Cholesky decomposition and solving the normal equation.

        1. Compute XT X:
        Multiply XT (transpose of X) with X. The result is a symmetric matrix that summarizes the relationships (correlations) between features.

        - Shape: (n x n), where n is the number of features.
        - Example:
            If X = [[1, 2], [3, 4], [5, 6]], then:
            XT X = [[35, 44], [44, 56]]

        2. Compute XT y:
        Multiply XT with y. This vector represents how strongly each feature is correlated with the target.

        - Shape: (n x 1) for single output y, or (n x k) for multivariate y.

        3. Add Regularization (alpha I):
        Add the scaled identity matrix alpha I to XT X to form the regularized matrix A:
        A = XT X + alpha I

        - I is an (n x n) identity matrix.
        - alpha controls the penalty on large coefficients, improving numerical stability.

        Step 4: Cholesky Decomposition
        ------------------------------
        This is the heart of the method, where the matrix A is decomposed into:
        A = L L^T
        Here, L is a lower triangular matrix.

        1. Positive Definiteness Check:
        During decomposition, each diagonal entry of L (L[i, i]) is computed as:
        L[i, i] = sqrt(A[i, i] - sum(L[i, :j]^2))
        If L[i, i] <= 0, A is not positive definite, and the decomposition fails.

        2. Fill Lower Triangular Matrix L:
        Off-diagonal elements are computed as:
        L[i, j] = (A[i, j] - sum(L[i, :j] * L[j, :j])) / L[j, j] (i > j)
        This iterative process builds L row by row.

        Step 5: Solving the Triangular Systems
        --------------------------------------
        Using L and L^T, solve the normal equation in two stages:

        1. Solve Lz = XT y for z:
        Use forward substitution, starting with the first equation in the system and solving sequentially.

        2. Solve L^T w = z for w:
        Use backward substitution, solving from the last equation backward.

        This yields the optimal weights w.

        Step 6: Compute Bias (Intercept)
        --------------------------------
        If fit_intercept is enabled, calculate the bias term b as:
        b = mean(y) - mean(X)^T w
        This ensures that the intercept captures the global offset between the features and target.

        Step 7: Error Handling
        ----------------------
        Throughout the process, the solver ensures robustness:
        - Positive Definiteness: Checks during decomposition ensure A is suitable for Cholesky.
        - Zero Division: Avoids division by zero in diagonal elements.
        - NaN/Infinity: Stops computation if invalid values are detected.
        """).strip()

            adv_lim = textwrap.dedent("""
        Solvers of RidgeRegression
        ==========================

        This documentation provides an overview of advantages and limitations of the solvers `lsqr`, `svd`, `cholesky`, and `Mini-Batch Stochastic Average Gradient (SAG)`,

        1. LSQR Solver
        ----------------
        The LSQR solver is an iterative method for solving large-scale, sparse linear systems or least-squares problems.

        Advantages:
        - Well-suited for large and sparse matrices.
        - Handles both overdetermined and underdetermined systems.
        - Does not require explicit matrix factorization.
        - Numerically stable and less sensitive to rounding errors.

        Limitations:
        - Can converge slowly for ill-conditioned systems.
        - Requires a matrix-vector product at each iteration, which may be computationally expensive for dense matrices.
        - Does not guarantee exact solutions for all problems, as it is iterative.

        2. SVD Solver (Singular Value Decomposition)
        ---------------------------------------------
        The SVD solver decomposes a matrix into singular values and vectors, solving linear systems using the pseudoinverse.

        Advantages:
        - Provides the most accurate solution for linear systems (numerical stability).
        - Handles rank-deficient matrices effectively.
        - Works well for ill-conditioned systems by regularizing small singular values.

        Limitations:
        - Computationally expensive (O(n³) complexity for dense matrices).
        - Not suitable for very large-scale problems due to memory and runtime limitations.
        - Requires explicit matrix decomposition, which may not be feasible for sparse matrices.

        3. Cholesky Solver
        --------------------
        The Cholesky solver is a direct method for solving positive definite linear systems using Cholesky factorization.

        Advantages:
        - Highly efficient for positive definite matrices.
        - Less computationally expensive than LU decomposition for specific problems.
        - Stable for well-conditioned matrices.

        Limitations:
        - Applicable only to positive definite matrices.
        - Fails if the matrix is not positive definite or near-singular.
        - Not suitable for sparse or large-scale matrices without specialized implementations.

        4. Mini-Batch Stochastic Average Gradient (SAG)
        -------------------------------------------------
        SAG is an optimization algorithm used primarily for convex problems, such as logistic regression or linear regression.

        Advantages:
        - Efficient for large-scale machine learning problems with a large number of samples.
        - Converges faster than simple stochastic gradient descent (SGD) due to variance reduction.
        - Scales well with the number of samples using mini-batches.

        Limitations:
        - Requires convexity of the objective function to guarantee convergence.
        - Performance depends on hyperparameter tuning (e.g., learning rate, batch size).
        - Sensitive to poorly conditioned problems.
        - Not suitable for small datasets due to overhead in mini-batch processing.
        """).strip()

            doc_map = {
                        "__lsqr_solver": lsqr_solver,
                        "lsqr_solver": lsqr_solver,
                        "_RidgeRegression__lsqr_solver": lsqr_solver,
                        "__lsqr": lsqr,
                        "lsqr": lsqr,
                        "_RidgeRegression__lsqr": lsqr,
                        "__sym_ortho": sym_ortho,
                        "sym_ortho": sym_ortho,
                        "_RidgeRegression__sym_ortho": sym_ortho,
                        "__svd_solver": svd_solver,
                        "svd_solver": svd_solver,
                        "_RidgeRegression__svd_solver": svd_solver,
                        "__svd": svd,
                        "svd": svd,
                        "_RidgeRegression__svd": svd,
                        "__mbsag_solver": mbsag_solver,
                        "mbsag_solver": mbsag_solver,
                        "_RidgeRegression__mbsag_solver": mbsag_solver,
                        "__compute_r2_score": compute_r2_score,
                        "compute_r2_score": compute_r2_score,
                        "_RidgeRegression__compute_r2_score": compute_r2_score,
                        "__compute_gradients": compute_gradients,
                        "compute_gradient": compute_gradients,
                        "_RidgeRegression__compute_gradient": compute_gradients,
                        "__compute_loss": compute_loss,
                        "compute_loss": compute_loss,
                        "_RidgeRegression__compute_loss": compute_loss,
                        "__cholesky_solver": cholesky_solver,
                        "cholesky_solver": cholesky_solver,
                        "_RidgeRegression__cholesky_solver": cholesky_solver,
                        "adv_lim": adv_lim,
                    }

            if not doc_name:
                raise ValueError("doc_name cannot be empty. Provide a valid doc_name.")
            try:
                return doc_map[doc_name]
            except KeyError:
                raise ValueError(f"model_analysis does not have anything called {doc_name}")
        except Exception as e:
            logger.info(f"Error in model_analysis: {e}")


    @staticmethod
    def demo():
        """
        This static method executes a comprehensive, self-contained demonstration of the `RidgeRegression` class using synthetic data.
        It is designed to serve as a "smoke test" to verify the integrity of the library and as an educational example for users
        to understand the model's workflow without writing any setup code.

        The `demo` method performs the following tasks:
        1. Dependency Verification: 
            - Checks if the external library `scikit-learn` is installed. This is required for data generation (`make_regression`), 
              splitting (`train_test_split`), and evaluation (`mean_squared_error`). 
            - If `scikit-learn` is missing, it logs an error message and terminates the demo gracefully.
        2. Data Generation: 
            - Creates a synthetic regression dataset with 10 samples, 5 features, and 1 target variables using `make_regression`.
            - Adds noise to the data to simulate real-world imperfections.
        3. Data Partitioning:
            - Splits the generated dataset into training (80%) and testing (20%) sets using `train_test_split` to simulate a standard machine learning pipeline.
        4. Model Initialization:
            - Instantiates a `RidgeRegression` model with `solver='mbsag'` (Mini-Batch Stochastic Average Gradient) and `calculation=True`.
            - Enabling `calculation` allows the user to see the internal mathematical steps and logging output during the process.
        5. Model Fitting:
            - Calls the `fit` method on the training data (`X_train`, `y_train`), triggering the iterative optimization process documented in the logs.
        6. Prediction & Evaluation:
            - Generates predictions on the unseen test set (`X_test`).
            - Computes the Mean Squared Error (MSE) between the predicted values and the actual values (`y_test`) to quantify model performance.
        
        Parameters:
        -----------
        None

        Returns:
        --------
        None
            This method does not return a value. It outputs logs and results directly to the console/logger.

        Raises:
        -------
        None
            ImportErrors are caught internally and logged as error messages.

        Usage:
        ------
            >>> from mlmechanica.regression.linear import RidgeRegression
            >>> RidgeRegression.demo()
        """
        try:
            from sklearn.datasets import make_regression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error
        except ImportError:
            logger.error("\033[91m\nError: This demo requires 'scikit-learn' installed.\033[0m")
            logger.error("\033[91mPlease run: pip install scikit-learn\033[0m")
            return

        logger.info("\n<---------------- Running RidgeRegression Demo ---------------->\n")
        
        logger.info("Step 1: Generating synthetic data (Samples=10, Features=5, Targets=1)...")
        X, y = make_regression(n_samples=10, n_features=5, n_targets=1, noise=5, random_state=42)

        logger.info("Step 2: Splitting data into Train (80%) and Test (20%)...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=3)

        logger.info("Step 3: Initializing RidgeRegression(solver='mbsag', calculation=True)...")
        model = RidgeRegression(solver='mbsag', calculation=True)

        logger.info("Step 4: Fitting the model...")
        model.fit(X_train, y_train)

        logger.info("Step 5: Predicting on test set...")
        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_true=y_test, y_pred=y_pred)
        logger.info(f"\n\nDemo Completed. Mean Squared Error (MSE): {mse:.4f}")
        logger.info("\n<-------------------------------------------------------------->\n")

