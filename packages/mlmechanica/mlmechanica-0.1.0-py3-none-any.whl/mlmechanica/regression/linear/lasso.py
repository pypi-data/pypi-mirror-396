import numpy as np
import sys
import textwrap
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class LassoRegression:
    """
    LassoRegression Class
    ===============================
    A custom implementation of Lasso Regression for educational purposes.
    This class demonstrates how Lasso Regression works with L1 regularization, enabling
    feature selection and penalization of model coefficients to prevent overfitting.

    Parameters:
    ----------
    alpha : float, optional, default=1.0
        The regularization strength parameter. Larger values apply greater L1 penalty,
        potentially driving coefficients to zero.

    max_iter : int, optional, default=1000
        The maximum number of iterations for the optimization algorithm to converge.
        Prevents the fitting process from running indefinitely.

    tol : float, optional, default=1e-4
        The tolerance for stopping criteria. The optimization process halts when the
        improvement in the solution is less than this threshold.

    fit_intercept : bool, optional, default=True
        Specifies whether to calculate the intercept for the model. If False, no intercept
        is used in the calculation.

    selection : {'cyclic', 'random'}, optional, default='cyclic'
        The feature update order in optimization. 'cyclic' updates features sequentially,
        while 'random' updates them randomly.

    random_state : int, np.random.Generator, or None, optional, default=None
        Seed or generator for random number generation. Ensures reproducibility when
        `selection='random'.

    early_stopping : bool, optional, default=False
        If True, stops the optimization process early when changes in model parameters
        fall below the tolerance `tol`.

    calculation : bool, optional, default=False
        A custom flag to trigger additional calculations or visualizations, based on
        specific implementation needs.

    Attributes:
    ----------
    weights : np.ndarray or None
        Coefficients for the regression model. Set during the `fit` process.

    bias : float or None
        The intercept term for the regression model, calculated if `fit_intercept=True`.

    feature_means_ : np.ndarray or None
        Mean of each feature, used for normalization when fitting the model.

    feature_stds_ : np.ndarray or None
        Standard deviation of each feature, used for normalization when fitting the model.

    _rng : np.random.Generator
        Internal random number generator, initialized with `random_state`.

    Raises:
    ----------
    ValueError:
        - If `alpha` is not a positive float.
        - If `selection` is neither 'cyclic' nor 'random'.

    Methods
    -------
        fit(X, y)
            Fits the Lasso Regression model to the training data.

            Parameters
            ----------
            X : array-like, shape (n_samples, n_features)
                The input data matrix containing features.
            y : array-like, shape (n_samples,)
                The target variable.

            Workflow
            --------
            1. Validates input dimensions.
            2. Normalizes features if `fit_intercept=True`.
            3. Uses coordinate descent to minimize the loss function with L1 regularization.
            4. Updates `weights` and `bias` based on calculated coefficients.

            Notes
            -----
            - Automatically centers the data if `fit_intercept=True`.
            - Uses cyclic or random feature update order based on `selection`.

        predict(X)
            Predicts target values for the given input data.

            Parameters
            ----------
            X : array-like, shape (n_samples, n_features)
                The input data matrix.

            Returns
            -------
            y_pred : array-like, shape (n_samples,)
                Predicted target values.

            Workflow
            --------
            y_pred = X @ weights + bias
            - Normalizes features using stored means and standard deviations.
            - Computes predictions using the learned weights and bias.

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
            Runs a self-contained demonstration/smoke test using synthetic data.

    Notes
    -----
    This implementation focuses on educational purposes, emphasizing the intuition and theory behind Lasso Regression.

    Example:
        >>> from mlmechanica.regression.linear import LassoRegression
        >>> model = LassoRegression(calculation=True)
    """
    def __init__(self, alpha=1.0, max_iter=1000, tol=1e-4, fit_intercept=True, 
                 selection='cyclic', calculation=False, random_state=None):
        
        if not isinstance(alpha, (int, float)) or alpha < 0:
            raise ValueError("Alpha must be a non-negative numeric value.")
        if not isinstance(max_iter, int) or max_iter <= 0:
            raise ValueError("max_iter must be a positive integer.")
        if not isinstance(tol, (int, float)) or tol <= 0:
            raise ValueError("tol must be a positive numeric value.")
        if not isinstance(fit_intercept, bool):
            raise TypeError("fit_intercept must be a boolean value.")
        if selection not in ['cyclic', 'random']:
            raise ValueError("selection must be either 'cyclic' or 'random'.")
        if random_state is not None and not isinstance(random_state, (int, np.random.Generator)):
            raise TypeError("random_state must be an integer or a NumPy Generator.")
        if not isinstance(calculation, bool):
            raise TypeError("calculation must be a boolean value.")

        self.alpha = float(alpha)
        self.max_iter = max_iter
        self.tol = tol
        self.fit_intercept = fit_intercept
        self.selection = selection
        self.random_state = random_state
        self.calculation = calculation
        
        self.coef_ = None
        self.intercept_ = 0.0
        self.feature_means_ = None
        self.feature_stds_ = None
        self._rng = np.random.default_rng(random_state)


    def _soft_threshold(self, rho, lam):
        if rho < -lam:
            return rho + lam
        elif rho > lam:
            return rho - lam
        else:
            return 0.0


    def fit(self, X, y):
        """
        Fit the model to the provided data using an iterative feature selection and weight update process.

        Parameters:
        ----------
        X : array-like of shape (n_samples, n_features)
            The training data, where `n_samples` is the number of samples and
            `n_features` is the number of features (columns).

        y : array-like of shape (n_samples,) or (n_samples, n_outputs)
            The target values corresponding to the samples in `X`. It can be a
            one-dimensional array for a single output or a two-dimensional array
            for multiple outputs.

        Returns:
        -------
        self : object
            Returns the instance of the model with fitted coefficients and intercepts.

        Attributes Updated:
        -------------------
        weights : array-like of shape (n_outputs, n_features)
            The weights (coefficients) for each feature after fitting the model.

        bias : array-like of shape (n_outputs,) or scalar
            The bias terms for each output variable after fitting the model.
            If `fit_intercept` is False, this will be set to 0.

        feature_means_ : array-like of shape (n_features,)
            The mean of each feature in `X`, used for normalization.

        feature_stds_ : array-like of shape (n_features,)
            The standard deviation of each feature in `X`, used for normalization.

        Raises:
        ------
        TypeError
            If either `X` or `y` is not a numpy array.

        ValueError
            If the number of samples in `X` and `y` do not match, or if any feature
            has zero variance, resulting in a division by zero.

        RuntimeError
            If an error occurs during the iterative fitting process, such as numerical instability.

        Notes:
        ------
        - This method performs feature scaling (normalization) before fitting the model.
        - If `fit_intercept` is True, an intercept term is included in the model.
        - The optimization loop updates the weights using a form of coordinate descent, where each
          feature's weight is adjusted based on its correlation with the residuals.
        - Regularization is applied during weight updates to enforce sparsity (L1 regularization).
        - The method supports early stopping based on the change in weights between iterations.
        - If early stopping is triggered or the maximum number of iterations is reached, the method
          returns the fitted model.

        Example:
            >>> import numpy as np
            >>> from mlmechanica.regression.linear import LassoRegression
            >>> X = np.array([1, 2, 3, 4, 5])
            >>> y = np.array([2, 4, 5, 4, 5])
            >>> model = LassoRegression()
            >>> model.fit(X, y)
        """
        if self.calculation:
            logger.info(f"<---------------- Fitting Lasso Regression ---------------->")

        X = np.asarray(X)
        y = np.asarray(y)

        if X.ndim != 2:
            raise ValueError("X must be a 2D array.")
        if y.ndim != 1:
            y = y.ravel()
        
        n_samples, n_features = X.shape

        if n_samples != y.shape[0]:
            raise ValueError("Number of samples in X and y must match.")

        if self.calculation:
            logger.info(f"\nDataset Shape: {X.shape}")
            if n_samples > 5:
                logger.info(f"First 5 rows of X:\n{X[:5]}")
                logger.info(f"First 5 rows of y:\n{y[:5]}")
            else:
                logger.info(f"X:\n{X}")
                logger.info(f"y:\n{y}")

        self.feature_means_ = np.mean(X, axis=0)
        self.feature_stds_ = np.std(X, axis=0)
        
        self.feature_stds_[self.feature_stds_ == 0] = 1.0

        X_scaled = (X - self.feature_means_) / self.feature_stds_
        
        y_mean = np.mean(y)
        y_centered = y - y_mean if self.fit_intercept else y

        if self.calculation:
            logger.info("\nStep 1: Data Normalization")
            logger.info(f"Feature Means: {self.feature_means_}")
            logger.info(f"Feature Stds:  {self.feature_stds_}")
            if self.fit_intercept:
                logger.info(f"Target Mean (to center y): {y_mean}")

        self.coef_ = np.zeros(n_features)
        
        residuals = y_centered - (X_scaled @ self.coef_)

        for iteration in range(self.max_iter):
            max_change = 0.0
            
            feature_order = self._rng.permutation(n_features) if self.selection == 'random' else range(n_features)

            if self.calculation and iteration < 3: 
                logger.info(f"\n--- Iteration {iteration + 1} ---")

            for j in feature_order:
                X_j = X_scaled[:, j]                
                old_weight = self.coef_[j]                
                residuals += old_weight * X_j                
                rho = np.dot(X_j, residuals)               
                normalization_factor = np.dot(X_j, X_j) 
                new_weight = self._soft_threshold(rho, self.alpha) / (normalization_factor + 1e-10)                
                self.coef_[j] = new_weight                
                residuals -= new_weight * X_j
                change = abs(old_weight - new_weight)
                max_change = max(max_change, change)

                if self.calculation and iteration == 0 and j < 3:
                    logger.info(f"\nFeature {j} Update:")
                    logger.info(f"  Rho (correlation with residual): {rho:.4f}")
                    logger.info(f"  Soft Thresholding applied with alpha={self.alpha}")
                    logger.info(f"  Old Weight: {old_weight:.4f} -> New Weight: {new_weight:.4f}")

            if max_change < self.tol:
                if self.calculation:
                    logger.info(f"\nConverged at iteration {iteration + 1} with max coefficient change {max_change:.6f}")
                break

        if self.fit_intercept:
            self.intercept_ = y_mean - np.dot(self.feature_means_ / self.feature_stds_, self.coef_)
        else:
            self.intercept_ = 0.0

        if self.calculation:
            logger.info(f"\nFinal Coefficients: {self.coef_}")
            logger.info(f"Final Intercept: {self.intercept_}")

        return self


    def predict(self, X):
        """
        Predict the target values for the provided input data.

        Parameters:
        ----------
        X : array-like of shape (n_samples, n_features)
            The input data for which predictions are to be made, where `n_samples` is
            the number of samples and `n_features` is the number of features.

        Returns:
        -------
        predictions : array-like of shape (n_samples,) or (n_samples, n_outputs)
            The predicted values corresponding to the input data `X`. The output shape
            will depend on whether the model is for single or multiple outputs.

        Raises:
        ------
        TypeError
            If `X` is not a NumPy array.

        ValueError
            If `X` is empty or if the number of features in `X` does not match the
            number of features used to train the model.

        AttributeError
            If the model is not properly initialized (i.e., if `feature_means_` or `weights`
            are not set).

        Notes:
        ------
        - The input data `X` is first standardized by subtracting the mean of each feature,
          which was computed during the training phase.
        - The predictions are computed using the formula `predictions = X.dot(weights.T) + bias`
          if `fit_intercept` is True. Otherwise, the formula is `predictions = X.dot(weights.T)`.
        - If the model has a single output, the predictions are flattened to a 1-dimensional array.
        - This method assumes that the model has already been fitted and that the necessary
          parameters (`weights`, `feature_means_`, and optionally `bias`) have been computed
          during training.
        - In case of an error during the prediction process, an exception is raised with an
          informative error message.

          Example:
            >>> X_new = np.array([6, 7])
            >>> predictions = model.predict(X_new)
            >>> print(predictions)
        """
        if self.calculation:
            logger.info(f"<---------------- Predicting ---------------->")

        X = np.asarray(X)
        if self.coef_ is None or self.feature_means_ is None:
            raise RuntimeError("Model is not fitted yet. Call 'fit' first.")
        
        if X.shape[1] != self.feature_means_.shape[0]:
            raise ValueError(f"Shape mismatch: X has {X.shape[1]} features, but model expects {self.feature_means_.shape[0]}.")

        X_scaled = (X - self.feature_means_) / self.feature_stds_

        if self.calculation:
            logger.info(f"\nApplying formula: y_pred = X_scaled @ coef + intercept")
            logger.info(f"First 5 rows of X_scaled:\n{X_scaled[:5]}")

        predictions = X_scaled @ self.coef_ + self.intercept_

        if self.calculation:
            logger.info(f"Predictions (first 5): {predictions[:5]}")

        return predictions


    def model_analysis(self, doc_name):
        """
        this method returns a detailed explanation or method based on the given `doc_name`.

        This method is used to retrieve specific methods or explanations based on the provided `doc_name` string.
        The method matches the `doc_name` against various predefined options, each representing a specific algorithm or method used in this class.
        If the `doc_name` is not recognized, an exception is raised.

        Parameters:
        -----------
        doc_name : str
            A string representing the name of the method or explanation to be returned.
            - implementation: Provides a general explanation about the class implementation.
            - objective: Provides a detailed explanation about the core objective of Lasso Regression.
            - loss_function: Provides a detailed explanation about the Least Squares Term (Loss Function) of Lasso Regression.
            - l1_reg: Provides a detailed explanation about the L1 Regularization Term in Lasso Regression.
            - coordinate_descent: Provides a detailed explanation about the Coordinate Descent Method.

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
            >>> from mlmechanica.regression.linear import LassoRegression
            >>> model = LassoRegression()
            >>> print(model.model_analysis('implementation'))

        """
        try:
            implementation = textwrap.dedent("""
            Lasso Regression Implementation Documentation
            ===========================================

            Purpose of the Model
            --------------------
            The model is solving a linear regression problem. It aims to find the weights (w) and biases (b)
            that minimize the prediction error between the observed values (y) and predicted values (y_hat):

                y_hat = X * w + b

            It also includes a regularization term to avoid overfitting by penalizing large weights.


            Preprocessing and Standardization
            ---------------------------------
            The model ensures the features (X) are standardized to have a mean of 0 and a standard deviation of 1. Mathematically:

                X_standardized = (X - mu_X) / (sigma_X + epsilon)

            - mu_X is the mean of each feature.
            - sigma_X is the standard deviation of each feature.
            - epsilon is a small number added to avoid division by zero.

            Reason: Standardization ensures that all features are on the same scale, making the optimization process more stable.


            Objective Function
            ------------------
            The model uses L1-regularized least squares regression. The objective is to minimize the following cost function:

                L(w, b) = (1 / 2m) * sum((y_i - y_hat_i)^2) + alpha * sum(|w_j|)

            - The first term is the mean squared error (MSE), which measures how close the predictions (y_hat_i) are to the actual values (y_i).
            - The second term, controlled by alpha, penalizes large coefficients (w_j) to enforce sparsity (many weights become zero).


            Coordinate Descent Optimization
            -------------------------------
            The weights (w) are optimized iteratively using a coordinate descent algorithm. This involves:

            1. Feature-wise Optimization:
                - For each feature j, compute its correlation (rho) with the residuals of the model:

                    rho_j = X_j^T * (y - y_hat) + w_j * (X_j^T * X_j)

                - X_j is the j-th column of X, and (y - y_hat) represents the residuals.

            2. Thresholding with Regularization:
                - Update w_j based on the value of rho_j:

                    w_j =
                    {
                        (rho_j + alpha) / (X_j^T * X_j), if rho_j < -alpha
                        (rho_j - alpha) / (X_j^T * X_j), if rho_j > alpha
                        0, if |rho_j| <= alpha
                    }

                - This ensures that small values of rho_j result in w_j = 0, enforcing sparsity.


            Bias Optimization
            -----------------
            If the model includes a bias term (b), it is updated separately by adjusting for the average of the residuals:

                b = b + mean(y - y_hat)

            Reason: The bias accounts for the overall offset in predictions.


            Convergence and Stopping Criteria
            ---------------------------------
            The optimization stops when the changes in weights (w) are below a threshold (tol), ensuring the model has converged.


            Predictions
            -----------
            After training, predictions are made as:

                y_hat = X_standardized * w + b

            If the model includes multiple targets (y in R^{m x k}), the process applies independently to each target.


            Mathematical Insights:
            ======================
            1. Regularization Effect:
                - The alpha * sum(|w_j|) term shrinks less important features to zero, reducing model complexity and improving generalization.

            2. Feature Sparsity:
                - Features with weak correlation (|rho_j| <= alpha) are eliminated, making the model interpretable.

            3. Iterative Optimization:
                - Each weight is updated independently, ensuring efficient computation even for high-dimensional data.

            4. Convergence:
                - The algorithm stops when the weights stabilize, ensuring a balance between accuracy and efficiency.

        """).strip()

            objective = textwrap.dedent("""
            Lasso Regression Objective: Explained
            =====================================

            This module explains the core objective of Lasso Regression, an extension of ordinary linear regression that introduces L1 regularization.
            The following sections break down the mathematical formulation, components of the objective function, and the role of regularization.

            ---

            1. Background: Linear Regression as an Optimization Problem
            -----------------------------------------------------------
            In ordinary linear regression, the goal is to find the coefficients β = (β1, β2, ......, βp) that minimize the sum of squared errors (SSE) between the predicted values ŷ and the true target values.
            The objective function is:
                L(β) = (1/2n) Σ(yᵢ - Σ(Xᵢⱼβⱼ))²

            Where:
            - `n`: The number of samples.
            - `p`: The number of features.
            - `Xᵢⱼ`: The value of the j-th feature for the i-th sample.

            Minimizing this function results in the coefficients β that best fit the data by reducing the error in predictions.

            ---

            2. Lasso Regression: Adding Regularization
            ------------------------------------------
            While linear regression works well in many cases, it has some limitations:
            - It doesn't inherently perform feature selection.
            - It can overfit, especially when there are many irrelevant or collinear features.

            Lasso Regression addresses these issues by adding an L1 regularization term to the objective function. The modified objective function becomes:

                L(β) = (1/2n) Σ(yᵢ - Σ(Xᵢⱼβⱼ))² + alpha Σ|βⱼ|

            This can also be written as:

                L(β) = (1/2n) ||y - Xβ||² + alpha ||β||₁

            Here:
            - `alpha`: A hyperparameter controlling the strength of the regularization.
            - `||β||₁`: The L1 norm of the coefficients, which is the sum of the absolute values of the coefficients.

            The addition of the L1 penalty term forces some of the coefficients to become exactly zero, helping with feature selection.

            ---

            3. Components of the Lasso Objective
            ------------------------------------
            The Lasso objective consists of two terms:

            (a) Least Squares Term (Loss Function):
                (1/2n) ||y - Xβ||²

            - This is the mean squared error (MSE) term.
            - It measures the error between the predicted values ŷ = Xβ and the true values y.
            - The goal of this term is to minimize prediction error.

            (b) L1 Regularization Term:
                alpha ||β||₁ = alpha Σ|βⱼ|

            - This term penalizes the magnitude of the coefficients β.
            - It imposes a penalty proportional to the absolute values of the coefficients |βⱼ|.
            - The hyperparameter `alpha` controls the strength of the penalty:
            - Higher alpha: Stronger regularization, which forces more coefficients to shrink to zero (stronger feature selection).
            - Lower alpha: Weaker regularization, making the model behave more like ordinary linear regression.

            ---

            4. Role of L1 Regularization
            -----------------------------
            L1 regularization plays a critical role in Lasso Regression's ability to perform feature selection.
            Unlike L2 regularization (used in Ridge Regression), which shrinks coefficients toward zero without making them exactly zero, L1 regularization can drive some coefficients βⱼ to exactly zero.
            This has two main benefits:

            1. Model Simplification:
            - By setting some coefficients to zero, Lasso Regression effectively removes the corresponding features from the model, making it easier to interpret.

            2. Avoiding Overfitting:
            - Reducing the complexity of the model helps prevent overfitting, especially when there are many features and fewer data points.

            ---

            5. Intuition Behind the L1 Norm
            -------------------------------
            - The L1 norm ||β||₁ sums the absolute values of the coefficients.
            - This creates a "diamond-shaped" constraint region when visualized geometrically.
            - During optimization, the solution β tends to lie on the edges or corners of the diamond, which leads to sparsity (many coefficients being exactly zero).

            ---

            6. Optimization Trade-off: Bias-Variance
            ----------------------------------------
            By adding the penalty term, Lasso Regression increases bias (because some coefficients are set to zero) but reduces variance (as the model is less sensitive to noisy data).
            The trade-off depends on the value of `alpha`:
            - A high `alpha` increases bias but helps reduce overfitting.
            - A low `alpha` reduces bias but may lead to overfitting.

            ---

            7. Final Objective Function
            ---------------------------
            To summarize, Lasso Regression aims to minimize the following objective function:

                Minimize: L(β) = (1/2n) ||y - Xβ||² + alpha Σ|βⱼ|

            This function balances:
            - Fitting the data through the least squares term, which minimizes prediction error.
            - Penalizing large coefficients and encouraging sparsity via the L1 regularization term.

            By tuning the hyperparameter `alpha`, Lasso Regression adapts to different datasets, selecting only the most relevant features while maintaining predictive accuracy.
        """).strip()

            loss_function = textwrap.dedent("""
            Least Squares Term (Loss Function) in Lasso Regression
            ====================================================

            The Least Squares Term is a key part of the objective function in linear regression
            models, including Lasso regression. It measures the difference between the actual
            target values and the predicted values.

            ---

            1. Expression of the Term
            -------------------------
            The Least Squares Term in Lasso Regression is expressed as:

                (1/2n) ||y - Xβ||² = (1/2n) Σ(yᵢ - ŷᵢ)²

            Where:
            - y = [y₁, y₂, ..., yₙ] : The actual target values (observations).
            - ŷᵢ = Σ(Xᵢⱼ * βⱼ) : The predicted target value for the i-th sample.
            - Xᵢⱼ : The value of the j-th feature for the i-th sample.
            - βⱼ : The model coefficient (weight) for the j-th feature.
            - X : The feature matrix. The size of X is n x p, where:
            - n : The number of samples (data points).
            - p : The number of features (variables).
            - β = [β₁, β₂, ..., βᵖ] : The model coefficients (weights) for each feature.
            - ||y - Xβ||₂² : The squared Euclidean norm of the residual vector. This represents
            the sum of squared differences between the actual and predicted target values.

            The Least Squares Term is the part of the objective function that ensures the model
            fits the data as accurately as possible.

            ---

            2. Purpose of the Term
            -----------------------
            The purpose of the Least Squares Term is to measure the model's error. It computes
            how far the predicted values (ŷ) are from the actual target values (y). The smaller
            this value is, the better the model fits the data.

            The goal of optimization is to minimize this term, ensuring that the model's
            predictions are as close as possible to the actual values.

            ---

            3. Why is it Called "Least Squares"?
            -----------------------------------
            The term "squares" comes from squaring the residuals (yᵢ - ŷᵢ).
            "Least" refers to the fact that the optimization process aims to minimize the sum
            of these squared residuals.

            The squaring of residuals ensures two things:
            1. Non-Negativity: All residuals (whether positive or negative) contribute equally to the loss.
            2. Penalizing Larger Errors: Larger residuals are penalized more heavily because of the squaring, which makes the model prioritize reducing significant prediction errors.

            ---

            4. Breaking it Down
            -------------------
            a) Residuals (yᵢ - ŷᵢ)
            - Residuals are the differences between the actual target values (yᵢ) and the predicted
            values (ŷᵢ):

                rᵢ = yᵢ - ŷᵢ

            - The residuals measure how well the model is performing for each data point:
            - A small residual indicates a good prediction.
            - A large residual indicates a poor prediction.

            b) Squared Residuals ((yᵢ - ŷᵢ)²)
            - Squaring the residuals ensures that all deviations contribute positively to the loss function.
            - Squaring also emphasizes larger errors, making the model focus more on reducing significant prediction errors.

            c) Averaging Over All Samples (1/n)
            - Dividing by n calculates the mean squared error (MSE).
            - This ensures that the loss function is normalized and can be applied to datasets of varying sizes.

            d) Scaling by 1/2
            - The factor of 1/2 is simply for convenience when calculating the derivative during optimization. It does not affect the final result but makes the optimization easier.

            ---

            5. Geometric Interpretation
            ---------------------------
            Geometrically, the Least Squares Term can be understood as follows:
            - The vector y represents the actual data in an n-dimensional space.
            - The vector ŷ = Xβ represents the predicted values from the linear model.
            - The vector of residuals r = y - ŷ represents the difference between the actual and predicted values.

            Minimizing the sum of squared residuals (||r||₂²) corresponds to finding the predicted values (ŷ) or the model coefficients (β) that make the residual vector (r) as small as possible.
            ---

            6. Least Squares in the Context of Lasso
            ----------------------------------------
            In Lasso Regression, the Least Squares Term plays the role of the data-fitting component.
            It ensures that the model's predictions are as close as possible to the actual values. However, Lasso adds a regularization term to control overfitting and perform feature selection.
        """).strip()

            l1_reg = textwrap.dedent("""
            L1 Regularization Term in Lasso Regression
            ==========================================

            1. Mathematical Definition of L1 Regularization
            -----------------------------------------------
            The L1 regularization term in Lasso Regression is given by:

            L1 Term = alpha * ||β||₁ = alpha * ∑|β_j|

            Where:
            - β_j are the coefficients of the model.
            - ||β||₁ represents the L1 norm, which is the sum of the absolute values of the coefficients.
            - alpha is a hyperparameter controlling the strength of the regularization.

            ---

            2. Purpose of L1 Regularization
            -------------------------------
            L1 regularization is added to the ordinary least squares (OLS) loss function to penalize large coefficients, reducing model complexity and preventing overfitting.
            It introduces sparsity in the model by encouraging many coefficients to become exactly zero, effectively performing feature selection.

        ---

            3. Geometric Interpretation of L1 Regularization
            ------------------------------------------------
            - When visualized geometrically, L1 regularization creates a diamond-shaped constraint region in coefficient space, as opposed to the circular constraint of L2 regularization (used in Ridge regression).
            - The solution to the optimization problem tends to lie on the edges or corners of this diamond, where some coefficients become exactly zero.
            - This characteristic of L1 regularization results in sparsity, where certain features are excluded from the model entirely.

            ---

            4. Effect of the Hyperparameter alpha
            ---------------------------------
            The regularization strength is controlled by the hyperparameter alpha:
            - alpha = 0: No regularization (OLS regression).
            - Increasing alpha: The penalty for large coefficients grows stronger, pushing more coefficients toward zero and resulting in greater sparsity.
            - Smaller alpha: The regularization effect weakens, allowing more coefficients to remain non-zero.

            The choice of alpha represents a trade-off between bias and variance:
            - Higher alpha: Increases bias (by shrinking coefficients more) but reduces variance, preventing overfitting.
            - Lower alpha: Reduces bias but may increase variance, risking overfitting.

            ---

            5. Lasso Regression and Feature Selection
            -----------------------------------------
            L1 regularization enables Lasso Regression to perform **feature selection** by driving some coefficients to exactly zero:
            - Features with weak predictive power are penalized more heavily, and their coefficients shrink towards zero.
            - As alpha increases, more coefficients become exactly zero, effectively removing less relevant features from the model.
            - This leads to a **sparse model** where only the most important features are retained, making the model simpler and more interpretable.
        """).strip()

            coordinate_descent = textwrap.dedent("""
            The Coordinate Descent
            ======================

            The coordinate descent method is an optimization algorithm often used to solve problems where the objective function f(x) is minimized over a vector x.
            Instead of optimizing all dimensions simultaneously, coordinate descent iteratively minimizes the function along one coordinate (variable) at a time, keeping the others fixed.
            It is particularly effective for high-dimensional problems or when f(x) is separable into functions of individual coordinates.

            Problem Statement
            -----------------
            We aim to minimize a multivariate objective function:
                min_{x in R^n} f(x),
            where x = (x_1, x_2, ..., x_n)^T and f(x) is differentiable and convex.

            Algorithm Overview
            ------------------
            At each step, the algorithm selects a coordinate i in {1, 2, ..., n}, and minimizes f(x) along that coordinate while keeping the others fixed:
                x_i^(k+1) = argmin_{x_i} f(x_1^(k), ..., x_{i-1}^(k), x_i, x_{i+1}^(k), ..., x_n^(k)).

            The updated value of x_i is then substituted back, and the process repeats until convergence.

            Mathematical Derivation
            -----------------------
            3.1 Univariate Minimization
            At iteration k, we have a current estimate x^(k). To minimize along coordinate i, we solve:
                x_i^(k+1) = argmin_{x_i} f(x_1^(k), ..., x_{i-1}^(k), x_i, x_{i+1}^(k), ..., x_n^(k)).
            Define the partial function g_i(x_i) as:
                g_i(x_i) = f(x_1^(k), ..., x_{i-1}^(k), x_i, x_{i+1}^(k), ..., x_n^(k)).
            Since g_i(x_i) is univariate, we solve:
                ∂g_i(x_i) / ∂x_i = 0 (first-order optimality condition).

            3.2 Iterative Updates
            The update rule for the i-th coordinate becomes:
                x_i^(k+1) = x_i^(k) - η * ∂g_i(x_i) / ∂x_i,
            where η > 0 is the step size (learning rate). For simplicity, exact line search can also be used to find x_i^(k+1).


            Convergence Analysis
            --------------------
            Coordinate descent works well when f(x) satisfies certain conditions, such as:
                1. Convexity: f(x) must be convex.
                2. Separability: f(x) can be decomposed into terms depending on individual coordinates:
                    f(x) = ∑_{i=1}^n f_i(x_i).

            Convergence Proof (Sketch)
            For convex functions:
                1. Decrease in Objective: At each step, the objective decreases:
                    f(x^(k+1)) ≤ f(x^(k)).
                2. Global Convergence: The sequence {x^(k)} converges to the global minimum x* because f(x) is convex and the updates reduce the function value.


            Advantages and Limitations
            --------------------------
            Advantages:
                - Efficient for high-dimensional problems.
                - Suitable for sparse or separable functions.

            Limitations:
                - Slow for functions with strong coupling between variables.
                - Convergence can be slow for non-separable problems.



            The Coordinate Descent Algorithm
            ================================

            The coordinate descent method involves iteratively optimizing one variable (or "coordinate") of the objective function f(x) at a time,
            while keeping all other variables fixed. This process is repeated cyclically or randomly over all coordinates until the algorithm converges.

            Initialization
            --------------
            - Objective Function: The goal is to minimize f(x), where x ∈ ℝⁿ is a vector of n variables: x = (x₁, x₂, ..., xₙ)ᵀ.
            - Starting Point: Initialize x⁰, a guess for the solution. This can be a zero vector, a random vector, or any feasible point.
            - Stopping Criteria: Define a convergence criterion, such as:
            - A maximum number of iterations.
            - A threshold on the norm of the gradient (e.g., ||∇f(x⁰)|| ≤ ε).
            - A small change in the function value between iterations (e.g., |f(x⁰⁺¹) - f(x⁰)| ≤ δ).


            Coordinate Selection
            --------------------
            At each iteration k, one coordinate i is selected for updating. The selection can be:
            - Cyclic: Traverse the coordinates sequentially, i.e., i = 1, 2, ..., n, and then repeat.
            - Randomized: Select a coordinate i uniformly at random at each step.
            - Greedy: Select the coordinate that results in the largest decrease in f(x).


            Univariate Optimization (Update Step)
            -------------------------------------
            For the chosen coordinate i, optimize the function f(x) with respect to xᵢ, keeping all other coordinates fixed.
            This reduces the problem to a univariate minimization problem:
                xᵢ⁰⁺¹ = argminₓᵢ f(x₁⁰, ..., xᵢ, ..., xₙ⁰).
            - Define a partial function gᵢ(xᵢ) by treating f(x) as a function of only xᵢ, with all other coordinates fixed:
                gᵢ(xᵢ) = f(x₁⁰, ..., xᵢ, ..., xₙ⁰).
            - Minimize gᵢ(xᵢ) to update xᵢ⁰⁺¹:
                ∇gᵢ(xᵢ) = 0 (solve for xᵢ⁰⁺¹).
            This update may require:
            - Closed-form solutions: For certain problems, the minimizer can be computed directly (e.g., quadratic objectives).
            - Numerical methods: If no closed-form solution exists, numerical solvers (e.g., Newton's method or gradient descent) may be used.


            Update the Solution Vector
            --------------------------
            Once xᵢ is updated, the solution vector becomes:
                x⁰⁺¹ = [x₁⁰, ..., xᵢ⁰⁺¹, ..., xₙ⁰]ᵀ.

            Iterative Process
            -----------------
            - Repeat the above steps (coordinate selection and univariate optimization) for all coordinates.
            If using cyclic selection, move to i = i+1 (mod n). If using random selection, pick a new i randomly.
            - After each coordinate update, f(x) decreases or remains constant (for convex f(x)).


            Convergence Criteria
            --------------------
            Stop the algorithm when one of the following conditions is met:
            1. Gradient Norm: The gradient ∇f(x) is small, indicating a critical point:
                ||∇f(x⁰⁺¹)|| ≤ ε.
            2. Change in Function Value: The change in f(x) between iterations is negligible:
                |f(x⁰⁺¹) - f(x⁰)| ≤ δ.
            3. Change in Variables: The change in x between iterations is small:
                ||x⁰⁺¹ - x⁰|| ≤ δ.
            4. Maximum Iterations: A predefined maximum number of iterations k_max is reached.



            Mathematical Derivation of Coordinate Descent
            =============================================

            Coordinate descent is an iterative optimization technique that minimizes a multivariable objective function f(x)
            by optimizing along one coordinate (variable) at a time while holding all other coordinates fixed.
            The core idea is to solve a sequence of one-dimensional optimization problems, one for each coordinate.

            In this section, we will derive and explain the detailed steps involved in the coordinate descent method mathematically.


            Problem Setup
            -------------

            We are given a convex and differentiable objective function f(x) where x = (x_1, x_2, ..., x_n)^T is an n-dimensional vector. Our goal is to find the vector x* that minimizes f(x):
            x* = argmin_{x in R^n} f(x).
            The function f(x) is typically assumed to be convex, meaning that any local minimum is also a global minimum.

            At iteration k, the current estimate of the solution is x^(k) = (x_1^(k), x_2^(k), ..., x_n^(k))^T.


            Coordinate Descent Update Rule
            ------------------------------

            In the coordinate descent method, we iteratively update the coordinates x_i one at a time, while fixing all the other coordinates.

            2.1. Univariate Minimization
            For each iteration k, we select a coordinate i in {1, 2, ..., n} (either cyclically or randomly) and
            minimize the objective function f(x) along the coordinate x_i, keeping the other coordinates fixed.

            Let us define the partial function g_i(x_i), where all coordinates except x_i are fixed at their current values from x^(k):
            g_i(x_i) = f(x_1^(k), x_2^(k), ..., x_{i-1}^(k), x_i, x_{i+1}^(k), ..., x_n^(k)).
            In this case, the function g_i(x_i) depends only on x_i, and the problem reduces to the univariate minimization:
            x_i^(k+1) = argmin_{x_i} g_i(x_i) = argmin_{x_i} f(x_1^(k), x_2^(k), ..., x_{i-1}^(k), x_i, x_{i+1}^(k), ..., x_n^(k)).
            Thus, to update x_i, we need to minimize the objective function with respect to x_i, holding all other coordinates fixed. This is the core idea of coordinate descent.

            2.2. First-Order Optimality Condition
            To find the optimal value x_i^(k+1) for coordinate i, we use the first-order optimality condition (necessary condition for a local minimum):
            ∂g_i(x_i) / ∂x_i = 0.
            This condition says that the gradient of the partial function g_i(x_i) with respect to x_i must vanish at the minimum.
            This is equivalent to solving the following equation for x_i:
            ∂f(x) / ∂x_i = 0 (with all other coordinates fixed).
            This is the key equation used in the update rule of coordinate descent.


            Line Search and Update Step
            ---------------------------

            In some cases, solving ∂f(x) / ∂x_i = 0 analytically might not be straightforward, so we can use a line search to find the optimal update for x_i.
            Specifically, we seek the value of x_i that minimizes f(x) in the direction of coordinate x_i, while fixing the other coordinates. This can be done as follows:

            1. Define the function g_i(x_i), as mentioned earlier.
            2. Perform a line search to find the value of x_i that minimizes g_i(x_i).

            The update for x_i^(k+1) can then be written as:
            x_i^(k+1) = x_i^(k) - η * ∂g_i(x_i) / ∂x_i,
            where η is the step size (also called learning rate), which controls how much we update x_i in the direction of the negative gradient.


            Complete Coordinate Descent Update
            ----------------------------------

            After solving the univariate optimization problem for x_i, we update the solution vector x^(k) by replacing the value of x_i^(k) with the newly computed value x_i^(k+1):
            x^(k+1) = (x_1^(k), x_2^(k), ..., x_{i-1}^(k), x_i^(k+1), x_{i+1}^(k), ..., x_n^(k)).
            This update is repeated for each coordinate i in {1, 2, ..., n}, either cyclically or randomly, until the algorithm converges.


            Convergence Conditions
            ----------------------

            For convex functions f(x), coordinate descent will converge to the global minimum under certain conditions,
            since the function decreases or remains constant after each update. However, for non-convex functions, the method may converge to a local minimum or a saddle point.

            To prove the convergence of coordinate descent, consider the following:
            - The function f(x) is convex, implying that the updates reduce the value of f(x) at each step.
            - Since coordinate descent only updates one coordinate at a time, the sequence of updates is guaranteed to converge to a local minimum.

            More formally, for a convex function f(x), the sequence of iterates {x^(k)} produced by coordinate descent satisfies:
            f(x^(k+1)) ≤ f(x^(k)),
            which means the objective function is non-increasing with each iteration. Under proper conditions, this leads to convergence.



            Coordinate Descent in Lasso Regression
            ======================================

            Lasso Regression is a form of linear regression that includes a penalty term to prevent overfitting and promote sparsity in the model by forcing
            some of the regression coefficients to be zero. The penalty term is proportional to the L1 norm of the regression coefficients.

            Lasso stands for Least Absolute Shrinkage and Selection Operator, and it addresses the problem of variable selection by shrinking less important coefficients to zero.
            This makes Lasso particularly useful when dealing with high-dimensional data, where many features may be irrelevant.

            We will now explain Coordinate Descent for Lasso Regression in great detail, including its mathematical derivation and the optimization steps involved.


            Lasso Regression Problem Setup
            ------------------------------

            The Lasso Regression optimization problem can be formulated as:
            min_{β} (1/2 ||y - Xβ||_2^2 + λ ||β||_1)

            where:
            - y ∈ R^m is the vector of target values.
            - X ∈ R^{m × n} is the feature matrix with m data points and n features.
            - β = (β_1, β_2, ..., β_n)^T ∈ R^n is the vector of regression coefficients.
            - ||y - Xβ||_2^2 = Σ_{i=1}^m (y_i - Σ_{j=1}^n X_{ij} β_j)^2 is the least squares error (squared Euclidean norm).
            - ||β||_1 = Σ_{j=1}^n |β_j| is the L1 norm of the coefficients, controlling the amount of shrinkage.
            - λ is the regularization parameter, controlling the strength of the L1 penalty (larger λ leads to more shrinkage).

            The goal is to find the vector β* that minimizes this objective function. The first term is the typical least squares loss,
            while the second term penalizes the absolute values of the coefficients to enforce sparsity.


            Coordinate Descent for Lasso Regression
            ---------------------------------------

            The coordinate descent method is a very effective technique for solving the Lasso regression problem because it allows us to update each coefficient β_j one at a time,
            while keeping the other coefficients fixed.

            The steps for solving the Lasso problem using coordinate descent are as follows:


            1. Update Rule for Each Coordinate
            ----------------------------------

            Let f(β) = (1/2 ||y - Xβ||_2^2 + λ ||β||_1) be the objective function we want to minimize.

            At each iteration k, the update for the coefficient β_j is given by minimizing the objective function with respect to β_j, while keeping the other coefficients β_i (for i ≠ j) fixed.

            The objective function can be written as:
            f_j(β_j) = (1/2 ||y - Xβ||_2^2 + λ |β_j|).


            2. Derivation of the Update Rule
            --------------------------------

            To find the optimal value of β_j, we first compute the partial derivative of f_j(β_j) with respect to β_j.
            The first term involves the least squares error, and the second term involves the L1 penalty.

            The least squares error term ||y - Xβ||_2^2 can be expanded as:
            ||y - Xβ||_2^2 = Σ_{i=1}^m (y_i - Σ_{j=1}^n X_{ij} β_j)^2.

            We focus on the part of the objective function that depends on β_j:
            ∂/∂β_j (1/2 ||y - Xβ||_2^2) = - X_j^T (y - Xβ),
            where X_j is the j-th column of the matrix X.

            The penalty term λ |β_j| contributes the derivative:
            ∂/∂β_j λ |β_j| = λ · sgn(β_j),
            where sgn(β_j) is the sign function, which returns 1 if β_j > 0, -1 if β_j < 0, and 0 if β_j = 0.

            Thus, the full gradient with respect to β_j is:
            ∂f(β)/∂β_j = - X_j^T (y - Xβ) + λ · sgn(β_j).

            To minimize f(β) with respect to β_j, we set the gradient equal to zero:
            - X_j^T (y - Xβ) + λ · sgn(β_j) = 0.

            Solving for β_j, we get the update rule for the coefficient β_j:
            β_j^{(k+1)} = S_λ ( X_j^T (y - X_{-j} β_{-j}) ),
            where X_{-j} represents the matrix X with the j-th column removed, and S_λ(z) is the soft-thresholding operator defined as:
            S_λ(z) = sgn(z) (|z| - λ)_+,
            where (|z| - λ)_+ = max(0, |z| - λ).

            This update rule means that we shrink the coefficient β_j by a value of λ (or set it to zero if |z| ≤ λ),
            and the direction of the shrinkage depends on the sign of X_j^T (y - X_{-j} β_{-j}).


            3. Complete Coordinate Descent Algorithm for Lasso
            --------------------------------------------------

            The coordinate descent algorithm for Lasso regression involves the following steps:

            1. Initialize β^{(0)} = (0, 0, ..., 0)^T (or any initial guess).
            2. For k = 0, 1, 2, ... (until convergence):
            - For each coordinate j = 1, 2, ..., n:
                1. Compute the partial residual r_j^{(k)} = y - Xβ^{(k)} + X_j β_j^{(k)}.
                2. Update β_j^{(k+1)} = S_λ ( X_j^T r_j^{(k)}) using the soft-thresholding rule.
            3. Repeat until convergence (the change in the objective function is below a threshold or the coefficients stop changing).


            4. Computational Complexity and Convergence
            -------------------------------------------

            - Computational Complexity: Each iteration involves updating each of the n coefficients, and each update requires computing the residuals
            and applying the soft-thresholding operator, which is computationally inexpensive (just a sign function and subtraction).
            Therefore, the overall computational complexity of each iteration is O(m · n), where m is the number of data points, and n is the number of features.

            - Convergence: Coordinate descent converges to a local minimum for Lasso regression under the assumption that the function is convex.
            Since the Lasso objective function is convex, coordinate descent is guaranteed to converge to a global minimum,
            provided that the updates are done properly(e.g., using a fixed or diminishing step size).
        """).strip()

            doc_map = {
                "implementation": implementation,
                "objective": objective,
                "loss_function": loss_function,
                "l1_reg": l1_reg,
                "coordinate_descent": coordinate_descent,
                }
            if doc_name is None:
                raise ValueError("doc_name cannot be empty. Give a doc_name")
            try:
                return doc_map[doc_name]
            except KeyError:
                raise ValueError(f"model_analysis does not have anything called {doc_name}")

        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr)
            raise


    @staticmethod
    def demo():
        """
        This static method executes a comprehensive, self-contained demonstration of the `LassoRegression` class using synthetic data.
        It is designed to serve as a "smoke test" to verify the integrity of the library and as an educational example for users
        to understand the Coordinate Descent workflow without writing any setup code.

        The `demo` method performs the following tasks:
        1. Dependency Verification: 
            - Checks if the external library `scikit-learn` is installed. This is required for data generation (`make_regression`), 
              splitting (`train_test_split`), and evaluation (`mean_squared_error`). 
            - If `scikit-learn` is missing, it logs an error message and terminates the demo gracefully.
        2. Data Generation: 
            - Creates a synthetic regression dataset with 10 samples, 5 features, and 1 target variable using `make_regression`.
            - Adds noise to the data to simulate real-world imperfections.
        3. Data Partitioning:
            - Splits the generated dataset into training (80%) and testing (20%) sets using `train_test_split`.
        4. Model Initialization:
            - Instantiates a `LassoRegression` model with `alpha=1.0` and `calculation=True`.
            - Enabling `calculation` allows the user to see the soft-thresholding and coordinate descent updates in the logs.
        5. Model Fitting:
            - Calls the `fit` method on the training data (`X_train`, `y_train`), triggering the iterative optimization process.
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
            >>> from mlmechanica.regression.linear import LassoRegression
            >>> LassoRegression.demo()
        """
        try:
            from sklearn.datasets import make_regression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error
        except ImportError:
            logger.error("\033[91m\nError: This demo requires 'scikit-learn' installed.\033[0m")
            logger.error("\033[91mPlease run: pip install scikit-learn\033[0m")
            return

        logger.info("\n<---------------- Running LassoRegression Demo ---------------->\n")
        
        logger.info("Step 1: Generating synthetic data (Samples=10, Features=5, Targets=1)...")
        X, y = make_regression(n_samples=10, n_features=5, n_targets=1, noise=5, random_state=42)

        logger.info("Step 2: Splitting data into Train (80%) and Test (20%)...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=3)

        logger.info("Step 3: Initializing LassoRegression(alpha=1.0, calculation=True)...")
        model = LassoRegression(alpha=1.0, calculation=True)

        logger.info("Step 4: Fitting the model...")
        model.fit(X_train, y_train)

        logger.info("Step 5: Predicting on test set...")
        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_true=y_test, y_pred=y_pred)
        logger.info(f"\n\nDemo Completed. Mean Squared Error (MSE): {mse:.4f}")
        logger.info("\n<-------------------------------------------------------------->\n")

