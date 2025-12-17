"""
CREATESONLINE Regression Algorithms

Pure Python regression implementations.
"""

import numpy as np
from typing import Union


class LinearRegression:
    """
    Linear Regression implementation using normal equation and gradient descent
    
    Pure Python implementation with numpy for matrix operations.
    """
    
    def __init__(self, learning_rate: float = 0.01, max_iterations: int = 1000, tolerance: float = 1e-6):
        """
        Initialize Linear Regression
        
        Args:
            learning_rate: Learning rate for gradient descent
            max_iterations: Maximum iterations for gradient descent
            tolerance: Convergence tolerance
        """
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
        self.weights = None
        self.bias = None
        self.cost_history = []
        self.fitted = False
    
    def fit(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list], method: str = 'normal_equation') -> 'LinearRegression':
        """
        Fit linear regression model
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,)
            method: 'normal_equation' or 'gradient_descent'
        
        Returns:
            Self for method chaining
        """
        # Convert to numpy arrays
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        # Ensure X is 2D
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples, n_features = X.shape
        
        if method == 'normal_equation':
            # Normal equation: θ = (X^T X)^(-1) X^T y
            try:
                # Add bias column
                X_with_bias = np.column_stack([np.ones(n_samples), X])
                
                # Calculate weights using normal equation
                XtX = X_with_bias.T @ X_with_bias
                Xty = X_with_bias.T @ y
                
                # Check if matrix is invertible
                if np.linalg.det(XtX) != 0:
                    weights_with_bias = np.linalg.solve(XtX, Xty)
                    self.bias = weights_with_bias[0]
                    self.weights = weights_with_bias[1:]
                else:
                    # Fallback to gradient descent if matrix is singular
                    return self.fit(X, y, method='gradient_descent')
                    
            except np.linalg.LinAlgError:
                # Fallback to gradient descent
                return self.fit(X, y, method='gradient_descent')
        
        elif method == 'gradient_descent':
            # Initialize weights and bias
            self.weights = np.random.normal(0, 0.01, n_features)
            self.bias = 0.0
            self.cost_history = []
            
            # Gradient descent
            for iteration in range(self.max_iterations):
                # Forward pass
                y_pred = X @ self.weights + self.bias
                
                # Calculate cost (MSE)
                cost = np.mean((y_pred - y) ** 2)
                self.cost_history.append(cost)
                
                # Calculate gradients
                dw = (2 / n_samples) * X.T @ (y_pred - y)
                db = (2 / n_samples) * np.sum(y_pred - y)
                
                # Update parameters
                self.weights -= self.learning_rate * dw
                self.bias -= self.learning_rate * db
                
                # Check for convergence
                if iteration > 0 and abs(self.cost_history[-2] - self.cost_history[-1]) < self.tolerance:
                    break
        
        else:
            raise ValueError("Method must be 'normal_equation' or 'gradient_descent'")
        
        self.fitted = True
        return self
    
    def predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features to predict on (n_samples, n_features)
        
        Returns:
            Predictions (n_samples,)
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before making predictions")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        return X @ self.weights + self.bias
    
    def score(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> float:
        """
        Calculate R-squared score
        
        Args:
            X: Features
            y: True targets
        
        Returns:
            R-squared score
        """
        y_pred = self.predict(X)
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        
        return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    
    def get_params(self) -> dict:
        """Get model parameters"""
        return {
            'weights': self.weights.tolist() if self.weights is not None else None,
            'bias': float(self.bias) if self.bias is not None else None,
            'learning_rate': self.learning_rate,
            'max_iterations': self.max_iterations,
            'tolerance': self.tolerance
        }


class LogisticRegression:
    """
    Logistic Regression implementation using gradient descent
    
    Pure Python implementation with numpy for matrix operations.
    """
    
    def __init__(self, learning_rate: float = 0.01, max_iterations: int = 1000, tolerance: float = 1e-6):
        """
        Initialize Logistic Regression
        
        Args:
            learning_rate: Learning rate for gradient descent
            max_iterations: Maximum iterations for gradient descent
            tolerance: Convergence tolerance
        """
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
        self.weights = None
        self.bias = None
        self.cost_history = []
        self.fitted = False
    
    @staticmethod
    def _sigmoid(z: np.ndarray) -> np.ndarray:
        """Sigmoid activation function"""
        # Clip z to prevent overflow
        z = np.clip(z, -500, 500)
        return 1 / (1 + np.exp(-z))
    
    def fit(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> 'LogisticRegression':
        """
        Fit logistic regression model
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,) - binary (0, 1)
        
        Returns:
            Self for method chaining
        """
        # Convert to numpy arrays
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        # Ensure X is 2D
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples, n_features = X.shape
        
        # Initialize weights and bias
        self.weights = np.random.normal(0, 0.01, n_features)
        self.bias = 0.0
        self.cost_history = []
        
        # Gradient descent
        for iteration in range(self.max_iterations):
            # Forward pass
            z = X @ self.weights + self.bias
            y_pred = self._sigmoid(z)
            
            # Calculate cost (cross-entropy)
            # Add small epsilon to prevent log(0)
            epsilon = 1e-15
            y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
            cost = -np.mean(y * np.log(y_pred) + (1 - y) * np.log(1 - y_pred))
            self.cost_history.append(cost)
            
            # Calculate gradients
            dw = (1 / n_samples) * X.T @ (y_pred - y)
            db = (1 / n_samples) * np.sum(y_pred - y)
            
            # Update parameters
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
            
            # Check for convergence
            if iteration > 0 and abs(self.cost_history[-2] - self.cost_history[-1]) < self.tolerance:
                break
        
        self.fitted = True
        return self
    
    def predict_proba(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Predict class probabilities
        
        Args:
            X: Features to predict on (n_samples, n_features)
        
        Returns:
            Probabilities for class 1 (n_samples,)
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before making predictions")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        z = X @ self.weights + self.bias
        return self._sigmoid(z)
    
    def predict(self, X: Union[np.ndarray, list], threshold: float = 0.5) -> np.ndarray:
        """
        Make binary predictions
        
        Args:
            X: Features to predict on (n_samples, n_features)
            threshold: Decision threshold
        
        Returns:
            Binary predictions (n_samples,)
        """
        probabilities = self.predict_proba(X)
        return (probabilities >= threshold).astype(int)
    
    def score(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> float:
        """
        Calculate accuracy score
        
        Args:
            X: Features
            y: True targets
        
        Returns:
            Accuracy score
        """
        y_pred = self.predict(X)
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        return np.mean(y_pred == y)
    
    def get_params(self) -> dict:
        """Get model parameters"""
        return {
            'weights': self.weights.tolist() if self.weights is not None else None,
            'bias': float(self.bias) if self.bias is not None else None,
            'learning_rate': self.learning_rate,
            'max_iterations': self.max_iterations,
            'tolerance': self.tolerance
        }


class PolynomialRegression:
    """
    Polynomial Regression implementation
    
    Uses LinearRegression with polynomial features.
    """
    
    def __init__(self, degree: int = 2, **linear_kwargs):
        """
        Initialize Polynomial Regression
        
        Args:
            degree: Degree of polynomial features
            **linear_kwargs: Arguments passed to LinearRegression
        """
        self.degree = degree
        self.linear_model = LinearRegression(**linear_kwargs)
        self.fitted = False
    
    def _create_polynomial_features(self, X: np.ndarray) -> np.ndarray:
        """Create polynomial features"""
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples, n_features = X.shape
        
        # For simplicity, only handle single feature polynomial for now
        if n_features == 1:
            poly_features = []
            for i in range(1, self.degree + 1):
                poly_features.append(X[:, 0] ** i)
            return np.column_stack(poly_features)
        else:
            # For multiple features, just use powers of each feature
            poly_features = [X]
            for degree in range(2, self.degree + 1):
                poly_features.append(X ** degree)
            return np.column_stack(poly_features)
    
    def fit(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> 'PolynomialRegression':
        """
        Fit polynomial regression model
        
        Args:
            X: Training features
            y: Training targets
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        poly_X = self._create_polynomial_features(X)
        
        self.linear_model.fit(poly_X, y)
        self.fitted = True
        return self
    
    def predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features to predict on
        
        Returns:
            Predictions
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before making predictions")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        poly_X = self._create_polynomial_features(X)
        
        return self.linear_model.predict(poly_X)
    
    def score(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> float:
        """
        Calculate R-squared score
        
        Args:
            X: Features
            y: True targets
        
        Returns:
            R-squared score
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        poly_X = self._create_polynomial_features(X)
        
        return self.linear_model.score(poly_X, y)


class RidgeRegression:
    """
    Ridge Regression (L2 regularization) implementation
    
    Pure Python implementation with numpy.
    """
    
    def __init__(self, alpha: float = 1.0, learning_rate: float = 0.01, max_iterations: int = 1000):
        """
        Initialize Ridge Regression
        
        Args:
            alpha: Regularization strength
            learning_rate: Learning rate for gradient descent
            max_iterations: Maximum iterations
        """
        self.alpha = alpha
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        
        self.weights = None
        self.bias = None
        self.fitted = False
    
    def fit(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> 'RidgeRegression':
        """
        Fit ridge regression model
        
        Args:
            X: Training features
            y: Training targets
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples, n_features = X.shape
        
        # Try normal equation approach first
        try:
            # Add bias column
            X_with_bias = np.column_stack([np.ones(n_samples), X])
            
            # Ridge normal equation: θ = (X^T X + αI)^(-1) X^T y
            XtX = X_with_bias.T @ X_with_bias
            
            # Add regularization (don't regularize bias term)
            reg_matrix = self.alpha * np.eye(n_features + 1)
            reg_matrix[0, 0] = 0  # Don't regularize bias
            
            XtX_reg = XtX + reg_matrix
            Xty = X_with_bias.T @ y
            
            weights_with_bias = np.linalg.solve(XtX_reg, Xty)
            self.bias = weights_with_bias[0]
            self.weights = weights_with_bias[1:]
            
        except np.linalg.LinAlgError:
            # Fallback to gradient descent
            self.weights = np.random.normal(0, 0.01, n_features)
            self.bias = 0.0
            
            for _ in range(self.max_iterations):
                y_pred = X @ self.weights + self.bias
                
                # Gradients with L2 regularization
                dw = (2 / n_samples) * X.T @ (y_pred - y) + 2 * self.alpha * self.weights
                db = (2 / n_samples) * np.sum(y_pred - y)
                
                self.weights -= self.learning_rate * dw
                self.bias -= self.learning_rate * db
        
        self.fitted = True
        return self
    
    def predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """Make predictions"""
        if not self.fitted:
            raise RuntimeError("Model must be fitted before making predictions")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        return X @ self.weights + self.bias
    
    def score(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> float:
        """Calculate R-squared score"""
        y_pred = self.predict(X)
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        
        return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0