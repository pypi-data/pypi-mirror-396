import numpy as np
import textwrap
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s', force=True)
logger = logging.getLogger(__name__)

class SimpleLinearRegression:
    """
    SimpleLinearRegression Class
    ============================
    A custom implementation of Simple Linear Regression for educational purposes.
    This class models the relationship between a single independent variable (feature) and 
    a dependent variable (target) using a linear equation. It provides a transparent, 
    from-scratch implementation of the Ordinary Least Squares (OLS) method.

    This class offers flexibility in visualizing the internal calculation steps (via the 
    `calculation` parameter) and provides analytical tools for understanding the model's 
    derivation and performance.

    Parameters:
    -----------
    calculation : bool, optional, default=False
        A flag to toggle detailed logging of calculations.
        - If True, the model logs intermediate steps (sums, numerator, denominator) 
          during the fitting process and formulas during prediction.
        - If False, the model runs silently (standard behavior).

    Attributes:
    -----------
    coef_ : float or None
        The slope (m) of the regression line. Represents the change in y for a 
        one-unit change in X. Initialized to None.

    intercept_ : float or None
        The y-intercept (b) of the regression line. Represents the value of y 
        when X is 0. Initialized to None.

    calculation : bool
        Stores the value of the `calculation` parameter.

    history : list
        Records the history of computed slope/intercept values (if applicable) 
        during the training process.

    Methods
    -------
    fit(X, y)
        Fits the Simple Linear Regression model to the training data.

        Parameters
        ----------
        X : numpy.ndarray, shape (n_samples,)
            The input feature array (independent variable).
        y : numpy.ndarray, shape (n_samples,)
            The target array (dependent variable).

        Workflow
        --------
        1. Validates input dimensions (must be 1D arrays).
        2. Calculates the mean of X (X̄) and y (ȳ).
        3. Computes the numerator Σ((X - X̄)(y - ȳ)) and denominator Σ((X - X̄)²)
           iteratively to demonstrate the summation process.
        4. Computes the slope: m = numerator / denominator.
        5. Computes the intercept: b = ȳ - mX̄.

    predict(X)
        Predicts target values for the given input data.

        Parameters
        ----------
        X : numpy.ndarray, shape (n_samples,)
            The input feature array.

        Returns
        -------
        y_pred : numpy.ndarray
            Predicted target values.

        Workflow
        --------
        y_pred = m * X + b

    model_analysis(doc_name)
        Provides theoretical and mathematical documentation.

        Parameters
        ----------
        doc_name : str
            - 'class_doc': General explanation of the model.
            - 'derivation': Mathematical derivation of OLS formulas.

    demo()
        Runs a self-contained demonstration/smoke test using synthetic data.

    Raises:
    -------
    ValueError:
        - If inputs X and y are not numpy arrays or have mismatched lengths.
    ZeroDivisionError:
        - If the variance of X is zero (denominator becomes 0).
    TypeError:
        - If `calculation` is not a boolean.        
    
    Notes
    -----
    This implementation focuses on educational purposes, emphasizing the intuition and theory behind Simple Linear Regression.

    Example:
        >>> from mlmechanica.regression.linear import SimpleLinearRegression
        >>> model = SimpleLinearRegression(calculation=True)
        >>> model.demo()
    """
    def __init__(self, calculation=False):
        if not isinstance(calculation, bool):
            raise TypeError(f"Expected 'calculation' to be of type bool, but got {type(calculation).__name__}")

        self.coef_ = None
        self.calculation = calculation
        self.intercept_ = None
        self.history = []


    def fit(self, X, y):
        """
        Fits the linear model to the provided data by calculating the slope (coef_) and intercept (intercept_).

        This method computes the slope (m) and intercept (b) of the linear regression model using the least squares method.
        It handles input validation, displays intermediate calculations if the `calculation` attribute is set to True,
        and ensures the correct shape and type of the input data.

        Args:
            X (numpy.ndarray): A one-dimensional numpy array representing the input features (independent variable).
            y (numpy.ndarray): A one-dimensional numpy array representing the target values (dependent variable).

        Raises:
            ValueError: If `X` or `y` are not numpy arrays or if they do not have the same number of elements.
            RuntimeError: If there is an error during the calculation of the numerator or denominator while computing the slope.
            ZeroDivisionError: If the denominator is zero, which would cause a division by zero error when calculating the slope.
            Exception: Any other unexpected errors during the fitting process.

        Attributes:
            coef_ (float): The slope (m) of the linear model, calculated from the input data.
            intercept_ (float): The intercept (b) of the linear model, calculated from the input data.
            calculation (bool): If set to True, the method will display the intermediate steps and calculations performed
                                during the fitting process. Default is False.
            history (list): Records the history of loss values or performance metrics during training.

        Notes:
            - The method automatically checks the dimensions of `X` and `y`. If they are not one-dimensional arrays,
              they will be forcefully reshaped.
            - If the `calculation` flag is set to True, intermediate steps in the calculation of the slope and intercept
              are printed, including the formulas, numerator, and denominator calculations.
            - The method uses the formula for the slope: m = Σ((X - X̄) * (y - ȳ)) / Σ((X - X̄)^2), and the formula for
              the intercept: b = ȳ - (m * X̄).
            - The method checks for division by zero when calculating the slope and raises a `ZeroDivisionError` if the
              denominator is zero.

        Example:
            >>> import numpy as np
            >>> from mlmechanica.regression.linear import SimpleLinearRegression
            >>> X = np.array([1, 2, 3, 4, 5])
            >>> y = np.array([2, 4, 5, 4, 5])
            >>> model = SimpleLinearRegression()
            >>> model.fit(X, y)
        """
        if not isinstance(X, np.ndarray) or not isinstance(y, np.ndarray):
            raise ValueError("X and y must be numpy arrays.")
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must have the same number of elements.")

        if X.ndim != 1:
            logger.warning("\033[93m[WARNING!!] X must be one-dimensional. Forcefully flattening X.\033[0m")
            X = X.ravel()

        if y.ndim != 1:
            logger.warning("\033[93m[WARNING!!] y must be one-dimensional. Forcefully flattening y.\033[0m")
            y = y.ravel()


        if self.calculation:
            logger.info("\nFormula for slope (m): m = Σ((X - X̄) * (y - ȳ)) / Σ((X - X̄)^2)")
            logger.info("\nFormula for intercept (b): b = ȳ - (m * X̄)")

        X_mean = X.mean()
        y_mean = y.mean()

        numerator = 0
        denominator = 0

        for i in range(len(X)):
            term_num = (X[i] - X_mean) * (y[i] - y_mean)
            term_den = (X[i] - X_mean) ** 2
            
            numerator += term_num
            denominator += term_den

            if self.calculation:
                logger.info(f"\nRow {i} Calculation:")
                logger.info(f"Numerator term ((X - X̄)*(y - ȳ)): {term_num}")
                logger.info(f"Denominator term ((X - X̄)^2): {term_den}")
                logger.info(f"Current Numerator Sum: {numerator}")
                logger.info(f"Current Denominator Sum: {denominator}")

        if self.calculation:
            logger.info(f"\nFinal Numerator (Σ((X - X̄) * (y - ȳ))): {numerator}")
            logger.info(f"Final Denominator (Σ((X - X̄)^2)): {denominator}")

        if denominator == 0:
            raise ZeroDivisionError("Denominator is zero, cannot compute slope.")

        self.coef_ = numerator / denominator
        self.intercept_ = y_mean - (self.coef_ * X_mean)
        
        return self


    def predict(self, X):
        """
        Predicts the dependent variable values for given independent variable values.

        Args:
            X (numpy.ndarray): The independent variable values to predict for (1D array).

        Returns:
            numpy.ndarray: Predicted dependent variable values.

        Raises:
            ValueError: If X is not a numpy array.
            ValueError: If the model is not fitted (coef_ or intercept_ is None).

        Example:
            >>> X_new = np.array([6, 7])
            >>> predictions = model.predict(X_new)
            >>> print(predictions)
        """
        if not isinstance(X, np.ndarray):
            raise ValueError("X must be a numpy array.")
        if self.coef_ is None or self.intercept_ is None:
            raise ValueError("Model is not fitted. Call the 'fit' method before making predictions.")

        if self.calculation:
            logger.info("\nUsing the formula: ŷ = m * X + b")
            logger.info(f"m = {self.coef_}, b = {self.intercept_}")

        predictions = self.coef_ * X + self.intercept_
        return predictions


    def model_analysis(self, doc_name=None):
        """
        Provides the documentation and derivation of the Simple Linear Regression model.

        This method returns detailed documentation about the Simple Linear Regression class, including an overview of the model,
        mathematical derivations for the slope and intercept, and the steps involved in making predictions. The user can request
        either the general class documentation or the mathematical derivation of the model by specifying the `doc_name`.

        Args:
            doc_name (str, optional): A string that specifies which documentation to return. It can either be:
                - 'class_doc': Returns the general documentation of the SimpleLinearRegression class.
                - 'derivation': Returns the mathematical derivation of the slope and intercept.

            Raises:
                ValueError: If `doc_name` is None or if it is neither 'class_doc' nor 'derivation'.
                Exception: Any other unexpected errors that may arise during the process of returning the requested documentation.

        Returns:
            str: The requested documentation as a string. This can either be:
                - The general class documentation (`class_doc`).
                - The mathematical derivation (`derivation`).

        Notes:
            - The method is designed to return two types of documentation:
                1. **class_doc**: Provides a general explanation of the Simple Linear Regression model, including the formulas for
                  calculating the slope and intercept, as well as their significance.
                2. **derivation**: Provides a step-by-step derivation of the formulas for the slope and intercept, explaining
                  how the model parameters are obtained by minimizing the residual errors.
            - If an invalid `doc_name` is provided, the method will raise a `ValueError` to indicate the issue.

        Example:
            >>> from mlmechanica.regression.linear import SimpleLinearRegression
            >>> model = SimpleLinearRegression()
            >>> print(model.model_analysis('class_doc'))
            >>> print(model.model_analysis('derivation'))
        """
        try:
            class_doc = textwrap.dedent("""
            SimpleLinearRegression Class Documentation
            ===========================================================================

            This class implements a simple linear regression model from scratch using numpy.
            It models the relationship between an independent variable (X) and a dependent variable (y)
            through the equation of a straight line:

                ŷ = mX + b

            where:
            - ŷ: Predicted value of the dependent variable.
            - m: Slope of the regression line.
            - b: Intercept of the regression line.

            Mathematical Overview

            1. Calculation of the Slope (m)
            --------------------------------------
            The slope (m) determines the rate of change of y with respect to X. It is calculated using:

                m = Σ((X - X̄) * (y - ȳ)) / Σ((X - X̄)²)

            Where:
            - X̄: Mean of the independent variable (X).
            - ȳ: Mean of the dependent variable (y).
            - Σ((X - X̄) * (y - ȳ)): Covariance between X and y, capturing how changes in X are associated with changes in y.
            - Σ((X - X̄)²): Variance of X, measuring the spread of X around its mean.

            The numerator represents the relationship between deviations in X and y from their means,
            while the denominator normalizes this relationship by the variability in X. The slope m
            represents the average change in y for a one-unit change in X.

            ---

            2. Calculation of the Intercept (b)
            ------------------------------------------
            The intercept (b) is calculated to ensure that the regression line passes through the
            point (X̄, ȳ), the means of the variables. It is given by:

                b = ȳ - (m * X̄)

            Where:
            - ȳ: Mean of the dependent variable (y).
            - m * X̄: The slope-adjusted mean of the independent variable (X).

            This ensures the regression line is anchored at the average values of X and y.
            ---
            """).strip()

            derivation=textwrap.dedent("""
            Derivation of Slope (m) and Intercept (b)
            ===========================================================================

            This documentation provides an explanation of how the slope (m) and intercept (b)
            of a Simple Linear Regression line are derived mathematically.

            Overview:
            ----------
            In simple linear regression, we try to model the relationship between a dependent variable (y)
            and an independent variable (X) using the equation of a straight line:

                y = mX + b

            Where:
                - y: The dependent variable (predicted value).
                - X: The independent variable.
                - m: The slope of the regression line.
                - b: The intercept of the regression line.

            The objective is to find the values of m (slope) and b (intercept) that minimize the
            sum of squared errors (or residuals) between the observed values (y_i) and the predicted values (ŷ_i).

            Step 1: Define the Residual Error Function
            -----------------------------------------------------------------------
            The residual error (E) is the difference between the actual observed value (y_i) and the predicted value (ŷ_i) for each data point:

                E = Σ(y_i - (mX_i + b))^2

            Where:
                - y_i: Actual observed value for the i-th data point.
                - X_i: Independent variable value for the i-th data point.
                - m: Slope of the line.
                - b: Intercept of the line.

            The objective is to minimize this error function to find the optimal values for m and b.

            Step 2: Minimize the Error Function Using Partial Derivatives
            -----------------------------------------------------------------------
            To minimize the error function E, we take the partial derivatives of E with respect to m and b, and set them equal to zero.

            Derivative with Respect to b:
            The derivative of the error function with respect to the intercept b is calculated as follows:

                ∂E/∂b = -2 Σ(y_i - (mX_i + b))

            Setting this equal to zero:

                Σ(y_i - (mX_i + b)) = 0

            Simplifying the expression:

                Σy_i = m ΣX_i + b * n

            Where:
                - n is the number of data points.

            By dividing both sides by n, we get:

                ȳ = mX̄ + b

            This gives the formula for the intercept b:

                b = ȳ - mX̄

            Where:
                - ȳ is the mean of y.
                - X̄ is the mean of X.

            Derivative with Respect to m:
            Next, we take the partial derivative of E with respect to the slope m:

                ∂E/∂m = -2 ΣX_i(y_i - (mX_i + b))

            Setting this equal to zero:

                ΣX_i * y_i = m ΣX_i^2 + b ΣX_i

            Substitute the formula for b (b = ȳ - mX̄) into this equation:

                ΣX_i * y_i = m ΣX_i^2 + (ȳ - mX̄) ΣX_i

            Step 3: Solve for m (Slope)
            -----------------------------------------------------------------------
            After simplifying, we arrive at the formula for the slope m:

                m = Σ(X_i - X̄)(y_i - ȳ) / Σ(X_i - X̄)^2

            Where:
                - Σ(X_i - X̄)(y_i - ȳ) represents the covariance between X and y.
                - Σ(X_i - X̄)^2 represents the variance of X.

            Final Equations:
            Using the above derivations, we obtain the final equations for slope (m) and intercept (b):

            1. Slope (m):
                m = Σ(X_i - X̄)(y_i - ȳ) / Σ(X_i - X̄)^2

            2. Intercept (b):
                b = ȳ - mX̄

            These two equations allow us to compute the line of best fit that minimizes the sum of squared errors between the observed and predicted values.

            Conclusion:
            - The slope (m) quantifies the relationship between the dependent and independent variables.
            - The intercept (b) represents the value of y when X is zero.
            - The regression line minimizes the sum of squared errors, providing the best fit to the data.

            ---

            3. Making Predictions (ŷ)
            -----------------------------------------------------------------------
            Once m (slope) and b (intercept) are computed, predictions for ŷ can be made for any
            new value of X using:

                ŷ = mX + b

            Here:
            - X: The independent variable values (input).
            - mX: Contribution of the slope.
            - b: Contribution of the intercept.

            This formula applies the learned relationship (slope and intercept) to predict the
            dependent variable for new independent variable values.

            ---

            """).strip()
            if doc_name is None:
                raise ValueError("doc_name cannot be empty. Give a doc_name")
            elif doc_name == "class_doc":
                return class_doc
            elif doc_name == "derivation":
                return derivation
            else:
                raise ValueError("Invalid doc_name. doc_name must be 'class_doc' or 'derivation'.")
        except Exception as e:
            print(f"Error in model_analysis: {e}")

    @staticmethod
    def demo():
        """
        This static method executes a comprehensive, self-contained demonstration of the `SimpleLinearRegression` class using synthetic data.
        It is designed to serve as a "smoke test" to verify the integrity of the library and as an educational example for users
        to understand the model's workflow for univariate regression without writing any setup code.

        The `demo` method performs the following tasks:
        1. Dependency Verification: 
            - Checks if the external library `scikit-learn` is installed. This is required for data generation (`make_regression`), 
              splitting (`train_test_split`), and evaluation (`mean_squared_error`). 
            - If `scikit-learn` is missing, it logs an error message and terminates the demo gracefully.
        2. Data Generation: 
            - Creates a synthetic regression dataset with 20 samples, 1 feature (univariate), and 1 target variable using `make_regression`.
            - Adds noise to the data to simulate real-world imperfections.
        3. Data Partitioning:
            - Splits the generated dataset into training (80%) and testing (20%) sets using `train_test_split`.
            - Flattens the input features to 1D arrays to suit the Simple Linear Regression requirement.
        4. Model Initialization:
            - Instantiates a `SimpleLinearRegression` model with `calculation=True`.
            - Enabling `calculation` allows the user to see the internal slope and intercept formulas being applied.
        5. Model Fitting:
            - Calls the `fit` method on the training data (`X_train`, `y_train`), calculating slope (m) and intercept (b).
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
            >>> from mlmechanica.regression.linear import SimpleLinearRegression
            >>> SimpleLinearRegression.demo()
        """
        try:
            from sklearn.datasets import make_regression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error
        except ImportError:
            logger.error("\033[91m\nError: This demo requires 'scikit-learn' installed.\033[0m")
            logger.error("\033[91mPlease run: pip install scikit-learn\033[0m")
            return

        logger.info("\n<---------------- Running SimpleLinearRegression Demo ---------------->\n")
        
        logger.info("Step 1: Generating synthetic data (Samples=20, Features=1, Targets=1)...")
        X, y = make_regression(n_samples=20, n_features=1, n_targets=1, noise=5, random_state=42)

        logger.info("Step 2: Splitting data into Train (80%) and Test (20%)...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=3)
        
        X_train, X_test = X_train.flatten(), X_test.flatten()

        logger.info("Step 3: Initializing SimpleLinearRegression(calculation=True)...")
        model = SimpleLinearRegression(calculation=True)

        logger.info("Step 4: Fitting the model...")
        model.fit(X_train, y_train)

        logger.info("Step 5: Predicting on test set...")
        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_true=y_test, y_pred=y_pred)
        logger.info(f"\n\nDemo Completed. Mean Squared Error (MSE): {mse:.4f}")
        logger.info("\n<-------------------------------------------------------------->\n")


