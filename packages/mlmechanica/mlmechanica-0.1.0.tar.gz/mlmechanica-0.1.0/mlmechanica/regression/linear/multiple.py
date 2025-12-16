import numpy as np
import textwrap
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s', force=True)
logger = logging.getLogger(__name__)

class MultipleLinearRegression:
    """
    MultipleLinearRegression Class
    ===============================
    A custom implementation of Multiple Linear Regression for educational purposes.
    This class is designed to provide in-depth insights into the workings of multiple regression algorithms.
    It offers flexibility in parameter tuning, a transparent training process, and analytical tools for understanding the model's performance.

    Parameters:
    ----------
    fit_intercept : bool, optional, default=True
        Specifies whether to calculate the intercept for the model. If set to False,
        no intercept will be used in the calculation.

    normalize : bool, optional, default=True
        If True, the regressors (independent variables) are normalized before fitting the model.
        This parameter is ignored when `fit_intercept` is False. Normalization scales the data
        to have mean 0 and unit variance.

    calculation : bool, optional, default=False
        A flag to toggle additional calculations or behaviors within the model. The specific
        purpose of this flag is left to be defined based on the implementation needs.

    Attributes:
    ----------
    fit_intercept : bool
        Stores the value of the `fit_intercept` parameter, indicating whether an intercept
        is to be included in the model.

    normalize : bool
        Stores the value of the `normalize` parameter, indicating whether normalization
        of features is applied.

    calculation : bool
        Stores the value of the `calculation` parameter, representing the toggle for
        additional behaviors.

    coefficients : array-like or None
        Placeholder for the coefficients of the regression model. Initially set to None
        until the model is fitted.

    intercept_ : float or None
        Placeholder for the intercept of the regression model. Initially set to None
        until the model is fitted.

    mean_ : array-like or None
        Placeholder for the mean of each feature, used for normalization. Initially set to None.

    std_ : array-like or None
        Placeholder for the standard deviation of each feature, used for normalization.
        Initially set to None.

    Raises:
    ----------
    ValueError:
        - If `normalize` or `fit_intercept` is not a boolean value.
        - If `verbose` or `calculation` is not a boolean value.

    Methods
    -------
        Methods
        -------
        fit(X, y)
            Fits the Multiple Linear Regression model to the training data.

            Parameters
            ----------
            X : array-like, shape (n_samples, n_features)
                The input data matrix containing features.
            y : array-like, shape (n_samples,)
                The target variable.

            Workflow
            --------
            1. Checks the dimensionality of the input data.
            2. Prepares the data matrix by adding a column of ones if `fit_intercept=True`.
            3. Calculates the optimal weights using the Normal Equation:
                weights = (XᵀX)⁻¹Xᵀy
            4. Updates `weights` and `bias` attributes based on the calculated coefficients.

            Notes
            -----
            - Automatically centers the data if `fit_intercept=True`.
            - Raises a ValueError if the matrix XᵀX is non-invertible.

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
            - Adds a column of ones to the input data if `fit_intercept=True`.
            - Computes predictions using the learned weights and bias.

        compute_loss(X, y)
            Computes the Mean Squared Error (MSE) loss for the given data.

            Parameters
            ----------
            X : array-like, shape (n_samples, n_features)
                The input data matrix.
            y : array-like, shape (n_samples,)
                The true target values.

            Returns
            -------
            loss : float
                The computed MSE loss.

            Formula
            -------
            Loss = Σ((y_true - y_pred)²) / n_samples

            Notes
            -----
            Useful for evaluating the quality of the model during training.

        model_analysis()
            Provides a theoretical and mathematical analysis of the Multiple Linear Regression model.

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
    This implementation focuses on educational purposes, emphasizing the intuition and theory behind Multiple Linear Regression.

    Example:
        >>> from mlmechanica.regression.linear import MultipleLinearRegression
        >>> model = MultipleLinearRegression(calculation=True)
    """
    def __init__(self, fit_intercept=True, normalize=True, calculation=False):
        # Validate input types and values
        if not isinstance(fit_intercept, bool):
            raise TypeError(f"Expected 'fit_intercept' to be of type bool, got {type(fit_intercept).__name__}.")

        if not isinstance(normalize, bool):
            raise TypeError(f"Expected 'normalize' to be of type bool, got {type(normalize).__name__}.")

        if not isinstance(calculation, bool):
            raise TypeError(f"Expected 'calculation' to be of type bool, got {type(calculation).__name__}.")

        # Assign attributes only if validations pass
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.calculation = calculation
        self.coefficients = None
        self.intercept_ = None
        self.mean_ = None
        self.std_ = None


    def fit(self, X, y):
        """
        Fit the linear regression model to the provided data.

        Parameters:
        ----------
        X : array-like of shape (n_samples, n_features)
            The training data, where `n_samples` is the number of samples
            and `n_features` is the number of features.

        y : array-like of shape (n_samples,)
            The target values corresponding to the samples in `X`.

        Returns:
        -------
        self : object
            Returns the instance of the model with fitted coefficients and intercept.

        Attributes Updated:
        -------------------
        coefficients : array-like
            The coefficients (θ1, θ2, ..., θn) of the regression model after fitting.

        intercept_ : float
            The intercept term (θ0) of the regression model after fitting.
            If `fit_intercept` is False, this will be set to 0.

        mean_ : array-like
            The mean of each feature in `X`, used for normalization if `normalize=True`.

        std_ : array-like
            The standard deviation of each feature in `X`, used for normalization if `normalize=True`.

        Raises:
        ------
        RuntimeError
            If an error occurs during input validation, normalization, augmentation, or computation
            of coefficients due to issues like incompatible data dimensions or numerical instability.

        TypeError
            If either `X` or `y` is not a numpy array.

        ValueError
            If the number of samples in `X` and `y` do not match.

        np.linalg.LinAlgError
            If the normal equation solution fails due to multicollinearity or an ill-conditioned matrix.

        Notes:
        ------
        - If `normalize` is True, the features in `X` are normalized to have a mean of 0 and unit variance.
        - If `fit_intercept` is True, an intercept term is added to the model by augmenting `X` with a column of ones.
        - The coefficients are computed using the normal equation: `coefficients = (X^T * X)^-1 * X^T * y`.
        - When `calculation` is True, intermediate steps in normalization, augmentation, and coefficient computation
        are printed for transparency and debugging purposes.

        Example:
            >>> import numpy as np
            >>> from mlmechanica.regression.linear import MultipleLinearRegression
            >>> X = np.array([1, 2, 3, 4, 5])
            >>> y = np.array([2, 4, 5, 4, 5])
            >>> model = MultipleLinearRegression()
            >>> model.fit(X, y)
        """

        X = np.asarray(X)
        y = np.asarray(y)

        if y.ndim == 1:
            y = y.reshape(-1, 1)

        if not isinstance(X, np.ndarray):
            raise TypeError("X must be a numpy array.")
        if not isinstance(y, np.ndarray):
            raise TypeError("y must be a numpy array.")
        if X.shape[0] != y.shape[0]:
            raise ValueError(f"X and y must have the same number of samples, but got {X.shape[0]} and {y.shape[0]}.")

        if self.normalize:
            self.mean_ = X.mean(axis=0)
            self.std_ = X.std(axis=0)
            
            self.std_[self.std_ == 0] = 1.0
            
            X = (X - self.mean_) / self.std_

            if self.calculation:
                logger.info("\nNormalizing the X:\n")
                logger.info(f"Step 1: taking mean of X column wise:\n{self.mean_}\n")
                logger.info(f"Step 2: standerizing the X column wise:\n{self.std_}\n")
                logger.info(f"Step 3: Normalized X = (X - mean of X) / standarized X:\n{X}\n")

        if self.fit_intercept:
            X = np.c_[np.ones((X.shape[0], 1)), X]
            if self.calculation:
                logger.info(f"\n\nAugmented X (with intercept): column wise added ones with X that is => np.c_[np.ones((X.shape[0], 1)), X]:\n{X}\n")

        XTX = X.T @ X
        XTy = X.T @ y

        try:
            self.coefficients = np.linalg.pinv(XTX) @ XTy
        except np.linalg.LinAlgError:
            raise RuntimeError("Singular matrix error: This dataset may have multicollinearity or be ill-conditioned.")

        if self.calculation:
            logger.info("\nCalculating the coefficients\n")
            logger.info(f"Step 1: Multiplying X and Transpose of X (XTX):\n{XTX}\n")
            logger.info(f"Step 2: Multiplying y and Transpose of X (XTy):\n{XTy}\n")
            logger.info(f"Step 3: Inversing XTX (XTX_inv):\n{np.linalg.pinv(XTX)}\n")
            logger.info(f"Step 4: Multiplying XTX_inv and XTy (coefficients):\n{self.coefficients}\n")

        if self.fit_intercept:
            self.intercept_ = self.coefficients[0, :]
            self.coefficients = self.coefficients[1:, :]
        else:
            self.intercept_ = np.zeros((1, y.shape[1]))

        if self.calculation:
            logger.info(f"\n\nFinal Intercept (θ0): {self.intercept_}")
            logger.info(f"\nFinal Coefficients (θ1, θ2, ...): {self.coefficients}")

        return self


    def predict(self, X):
        """
        Predict target values for given input data using the fitted linear regression model.

        Parameters:
        ----------
        X : array-like of shape (n_samples, n_features)
            The input data for which predictions are to be made. `n_samples` is the number
            of samples, and `n_features` is the number of features.

        Returns:
        -------
        y_pred : array-like of shape (n_samples,)
            The predicted target values corresponding to the input data `X`.

        Raises:
        ------
        RuntimeError
            - If the model has not been fitted prior to prediction.
            - If an error occurs during normalization, augmentation, or prediction computation.

        Notes:
        ------
        - If `normalize` is True, the input features are normalized using the mean and standard
        deviation computed during fitting.
        - If `fit_intercept` is True, an intercept term is added to the input data by augmenting
        `X` with a column of ones.
        - The predictions are computed as the dot product of the augmented `X` and the model's coefficients.
        - When `calculation` is True, intermediate steps for normalization, augmentation, and prediction
        computation are printed for transparency and debugging purposes.

        Example:
            >>> X_new = np.array([6, 7])
            >>> predictions = model.predict(X_new)
            >>> print(predictions)
        """

        X = np.asarray(X)

        if self.normalize:
            if self.mean_ is None or self.std_ is None:
                raise RuntimeError("Model has not been fitted yet.")
            
            X = (X - self.mean_) / self.std_
            
            if self.calculation:
                logger.info("\nNormalizing the X:\n")
                logger.info(f"Step 1: taking mean of X column wise:\n{self.mean_}\n")
                logger.info(f"Step 2: standerizing the X column wise:\n{self.std_}\n")
                logger.info(f"Step 3: Normalized X = (X - mean of X) / standarized X:\n{X}\n")

        if self.fit_intercept:
            X = np.c_[np.ones((X.shape[0], 1)), X]
            if self.calculation:
                logger.info(f"\n\nAugmented X (with intercept): column wise added ones with X that is => np.c_[np.ones((X.shape[0], 1)), X]:\n{X}\n")

        prediction = X @ np.r_[self.intercept_.reshape(1, -1), self.coefficients]

        if self.calculation:
            logger.info(f"\nPrediction: Multiplying X and coefficients:\n{prediction}\n\n")

        return prediction


    def model_analysis(self, doc_name=None):
        """
        this method returns a detailed explanation or method based on the given `doc_name`.

        This method is used to retrieve specific methods or explanations based on the provided `doc_name` string.
        The method matches the `doc_name` against various predefined options, each representing a specific solver, algorithm, or function used in this class.
        If the `doc_name` is not recognized, an exception is raised.

        Parameters:
        -----------
        doc_name : str
            A string representing the name of the method or explanation to be returned.
            - class_doc: Returns the information about the class
            - derivation: Returns the derivation of the class

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
            >>> from mlmechanica.regression.linear import MultipleLinearRegression
            >>> model = MultipleLinearRegression()
            >>> print(model.model_analysis('class_doc'))
        """
        try:
            class_doc=textwrap.dedent("""
            Multiple Linear Regression Implementation Documentation
            ========================================================

            This module implements Multiple Linear Regression using the Normal Equation,
            a direct method for solving linear systems. The following sections describe
            the mathematical foundation, model setup, and computations involved.

            ---

            Model Equation:
            ---------------
            Multiple Linear Regression models the relationship between a target variable `y`
            and multiple input features `X` using the following equation:

                y = Xθ + ε

            Where:
            - `y`: Vector of target values (n x 1), where `n` is the number of samples.
            - `X`: Feature matrix (n x m), where `m` is the number of features.
            - `θ`: Vector of coefficients/parameters to be estimated (m x 1).
            - `ε`: Error term (random noise).

            The goal is to determine the optimal coefficients `θ` that minimize the sum of
            squared residuals between the predicted and actual target values.

            ---

            Normal Equation:
            ----------------
            The coefficients `θ` are computed using the **Normal Equation**:

                θ = (XᵀX)⁻¹Xᵀy

            Where:
            - `Xᵀ`: Transpose of the feature matrix `X`.
            - `(XᵀX)⁻¹`: Inverse of the square matrix resulting from the dot product of `Xᵀ` and `X`.
            - `Xᵀy`: Dot product of `Xᵀ` and the target vector `y`.

            The Normal Equation provides the solution by minimizing the cost function:

                J(θ) = (1/2n) Σ(yᵢ - ŷᵢ)²

            Where:
            - `J(θ)`: Cost function (Mean Squared Error).
            - `yᵢ`: Actual target value for sample `i`.
            - `ŷᵢ`: Predicted target value for sample `i`.
            - `n`: Total number of samples.

            ---
            """).strip()

            derivation = textwrap.dedent("""

            Multiple Linear Regression: Derivation of the Normal Equation
            =============================================================

            This documentation provides a step-by-step derivation of the Normal Equation for
            Multiple Linear Regression, which is used to compute the optimal parameters (θ)
            for the model. The derivation is based on minimizing the Mean Squared Error (MSE)
            cost function.

            ---

            1. Define the Objective Function
            -----------------------------------
            The goal of Multiple Linear Regression is to minimize the error between predicted
            values (ŷ) and actual values (y). The predicted values are given by:

                ŷ = Xθ

            Where:
            - `X` is the feature matrix (n x m), with `n` samples and `m` features.
            - `θ` is the vector of coefficients (m x 1).

            The residuals (or errors) are defined as the difference between the actual and
            predicted values:

                Error = y - ŷ = y - Xθ

            The cost function, also known as the Sum of Squared Errors (SSE), is defined as:

                J(θ) = ||y - Xθ||² = (y - Xθ)ᵀ (y - Xθ)

            This cost function quantifies how well the model fits the data. We aim to minimize
            this cost function with respect to the model parameters `θ`.

            ---

            2. Expand the Cost Function
            --------------------------------
            We expand the quadratic form of the cost function:

                J(θ) = (yᵀ - θᵀ Xᵀ)(y - Xθ)

            Using the distributive property of matrix multiplication, we get:

                J(θ) = yᵀ y - yᵀ Xθ - θᵀ Xᵀ y + θᵀ Xᵀ Xθ

            Since yᵀ Xθ and θᵀ Xᵀ y are scalars (and scalars are equal to their transposes),
            we combine them:

                J(θ) = yᵀ y - 2θᵀ Xᵀ y + θᵀ Xᵀ Xθ

            This is the expanded form of the cost function, which we aim to minimize.

            ---

            3. Differentiate to Minimize
            ---------------------------------
            To find the value of `θ` that minimizes the cost function, we take the derivative
            of `J(θ)` with respect to `θ`:

                ∂J(θ)/∂θ = ∂/∂θ [ yᵀ y - 2θᵀ Xᵀ y + θᵀ Xᵀ Xθ ]

            - The derivative of the constant term `yᵀ y` is 0.
            - The derivative of `-2θᵀ Xᵀ y` is `-2Xᵀ y`.
            - The derivative of `θᵀ Xᵀ Xθ` is `2Xᵀ Xθ` (using matrix calculus).

            Thus, the gradient is:

                ∂J(θ)/∂θ = -2Xᵀ y + 2Xᵀ Xθ

            ---

            4. Set the Derivative to Zero
            ----------------------------------
            To minimize `J(θ)`, we set the derivative to zero:

                -2Xᵀ y + 2Xᵀ Xθ = 0

            Simplifying:

                Xᵀ Xθ = Xᵀ y

            This equation represents the condition for the optimal parameters `θ`.

            ---

            5. Solve for θ
            -------------------
            Assuming `Xᵀ X` is invertible (non-singular), we can solve for `θ` by multiplying
            both sides of the equation by the inverse of `Xᵀ X`:

                θ = (Xᵀ X)⁻¹ Xᵀ y

            This is the Normal Equation, which gives the solution for the optimal coefficients
            `θ` in terms of the feature matrix `X` and target vector `y`.

            ---

            6. Interpretation
            ----------------------
            - `Xᵀ X`: This term represents the covariance matrix of the features. It captures
              the relationship between the features in the data.
            - `(Xᵀ X)⁻¹`: The inverse adjusts for scaling and ensures a solution exists.
            - `Xᵀ y`: This term captures the relationship between the features `X` and the
              target `y`.

            The solution provided by the Normal Equation gives the vector of coefficients `θ`
            that minimizes the error in the linear regression model, resulting in the best fit
            to the data.

            ---

            7. Handling Singular Matrices
            ----------------------------------
            If `Xᵀ X` is not invertible, typically due to multicollinearity (i.e., when some
            features are linearly dependent), the Normal Equation cannot be solved directly.
            In such cases, we use the **pseudo-inverse** of `Xᵀ X` instead. This generalizes
            the solution for cases where the inverse does not exist:

                θ = (Xᵀ X)⁻¹ Xᵀ y

            This approach provides a solution even when the matrix `Xᵀ X` is singular, ensuring
            that a valid solution can still be computed.

            ---

            Intercept (Bias) Term:
            ----------------------
            To include an intercept term (bias) in the model, the feature matrix `X` is
            augmented with a column of ones. This ensures that the model can capture the
            intercept without altering the matrix dimensions:

                X_b = [1, X]

            The updated Normal Equation becomes:

                θ = (X_bᵀX_b)⁻¹X_bᵀy

            Here, `X_b` represents the augmented feature matrix with the intercept term.

            ---

            Feature Normalization (Optional):
            ---------------------------------
            Feature normalization is an optional preprocessing step that ensures all features
            are on a similar scale. This is particularly useful for datasets where the features
            have widely varying ranges.

            The normalization formula is:

                X_normalized = (X - μ) / sigma

            Where:
            - `μ`: Mean of each feature (column-wise).
            - `sigma`: Standard deviation of each feature (column-wise).

            This transformation helps improve numerical stability and prevents one feature
            from dominating the model due to its scale.

            ---

            Prediction Equation:
            ---------------------
            Once the coefficients `θ` are computed, predictions for new input data `X` are
            made using the following equation:

                ŷ = Xθ

            If the intercept is included:

                ŷ = X_bθ

            Where:
            - `ŷ`: Predicted values.
            - `X_b`: Augmented feature matrix with the intercept term.
            - `θ`: Vector of coefficients (including the intercept).

            ---
            """).strip()

            doc_map = {
                "class_doc": class_doc,
                "derivation": derivation,
                }

            if doc_name is None:
                raise ValueError("doc_name cannot be empty. Give a doc_name")
            try:
                output = doc_map[doc_name]

                if 'google.colab' in sys.modules:
                    return output

                else:
                    try:
                        sys.stdout.reconfigure(encoding='utf-8')
                    except AttributeError:
                        pass
                    return output

            except KeyError:
                raise ValueError(f"model_analysis does not have anything called {doc_name}")
        except Exception as e:
            print(f"Error in model_analysis: {e}")


    @staticmethod
    def demo():
        """
        This static method executes a comprehensive, self-contained demonstration of the `MultipleLinearRegression` class using synthetic data.
        It is designed to serve as a "smoke test" to verify the integrity of the library and as an educational example for users
        to understand the model's workflow for multivariate regression without writing any setup code.

        The `demo` method performs the following tasks:
        1. Dependency Verification: 
            - Checks if the external library `scikit-learn` is installed. This is required for data generation (`make_regression`), 
              splitting (`train_test_split`), and evaluation (`mean_squared_error`). 
            - If `scikit-learn` is missing, it logs an error message and terminates the demo gracefully.
        2. Data Generation: 
            - Creates a synthetic regression dataset with 10 samples, 3 features (multivariate), and 1 target variable using `make_regression`.
            - Adds noise to the data to simulate real-world imperfections.
        3. Data Partitioning:
            - Splits the generated dataset into training (80%) and testing (20%) sets using `train_test_split`.
        4. Model Initialization:
            - Instantiates a `MultipleLinearRegression` model with `calculation=True`.
            - Enabling `calculation` allows the user to see the Normal Equation or Gradient Descent steps (depending on implementation).
        5. Model Fitting:
            - Calls the `fit` method on the training data (`X_train`, `y_train`).
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
            >>> from mlmechanica.regression.linear import MultipleLinearRegression
            >>> MultipleLinearRegression.demo()
        """
        try:
            from sklearn.datasets import make_regression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error
        except ImportError:
            logger.error("\033[91m\nError: This demo requires 'scikit-learn' installed.\033[0m")
            logger.error("\033[91mPlease run: pip install scikit-learn\033[0m")
            return

        logger.info("\n<---------------- Running MultipleLinearRegression Demo ---------------->\n")
        
        logger.info("Step 1: Generating synthetic data (Samples=10, Features=3, Targets=1)...")
        X, y = make_regression(n_samples=10, n_features=3, n_targets=1, noise=5, random_state=42)

        logger.info("Step 2: Splitting data into Train (80%) and Test (20%)...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=3)

        logger.info("Step 3: Initializing MultipleLinearRegression(calculation=True)...")
        model = MultipleLinearRegression(calculation=True)

        logger.info("Step 4: Fitting the model...")
        model.fit(X_train, y_train)

        logger.info("Step 5: Predicting on test set...")
        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_true=y_test, y_pred=y_pred)
        logger.info(f"\n\nDemo Completed. Mean Squared Error (MSE): {mse:.4f}")
        logger.info("\n<-------------------------------------------------------------->\n")


