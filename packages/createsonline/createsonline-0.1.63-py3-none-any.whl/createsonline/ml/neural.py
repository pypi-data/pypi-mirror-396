"""
CREATESONLINE Neural Networks

Pure Python neural network implementation.
"""

import numpy as np
from typing import List, Optional, Union, Tuple
import random


class NeuralNetwork:
    """
    Multi-layer Neural Network implementation
    
    Pure Python feedforward neural network with backpropagation.
    """
    
    def __init__(
        self,
        hidden_layers: List[int] = [10],
        activation: str = 'relu',
        output_activation: str = 'linear',
        learning_rate: float = 0.01,
        max_iterations: int = 1000,
        tolerance: float = 1e-6,
        random_state: Optional[int] = None,
        batch_size: Optional[int] = None
    ):
        """
        Initialize Neural Network
        
        Args:
            hidden_layers: List of hidden layer sizes
            activation: Activation function ('relu', 'sigmoid', 'tanh')
            output_activation: Output activation ('linear', 'sigmoid', 'softmax')
            learning_rate: Learning rate for gradient descent
            max_iterations: Maximum training iterations
            tolerance: Convergence tolerance
            random_state: Random seed for reproducibility
            batch_size: Batch size for mini-batch gradient descent (None for full batch)
        """
        self.hidden_layers = hidden_layers
        self.activation = activation
        self.output_activation = output_activation
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.random_state = random_state
        self.batch_size = batch_size
        
        self.weights = []
        self.biases = []
        self.loss_history = []
        self.fitted = False
        
        # Set random seed
        if self.random_state is not None:
            np.random.seed(self.random_state)
            random.seed(self.random_state)
    
    def _initialize_weights(self, n_features: int, n_outputs: int):
        """Initialize network weights and biases"""
        layers = [n_features] + self.hidden_layers + [n_outputs]
        
        self.weights = []
        self.biases = []
        
        for i in range(len(layers) - 1):
            # Xavier initialization
            limit = np.sqrt(6.0 / (layers[i] + layers[i + 1]))
            weight = np.random.uniform(-limit, limit, (layers[i], layers[i + 1]))
            bias = np.zeros((1, layers[i + 1]))
            
            self.weights.append(weight)
            self.biases.append(bias)
    
    def _relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation function"""
        return np.maximum(0, x)
    
    def _relu_derivative(self, x: np.ndarray) -> np.ndarray:
        """ReLU derivative"""
        return (x > 0).astype(float)
    
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Sigmoid activation function"""
        # Clip to prevent overflow
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))
    
    def _sigmoid_derivative(self, x: np.ndarray) -> np.ndarray:
        """Sigmoid derivative"""
        s = self._sigmoid(x)
        return s * (1 - s)
    
    def _tanh(self, x: np.ndarray) -> np.ndarray:
        """Tanh activation function"""
        return np.tanh(x)
    
    def _tanh_derivative(self, x: np.ndarray) -> np.ndarray:
        """Tanh derivative"""
        return 1 - np.tanh(x) ** 2
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax activation function"""
        # Subtract max for numerical stability
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def _activation_function(self, x: np.ndarray, activation: str) -> np.ndarray:
        """Apply activation function"""
        if activation == 'relu':
            return self._relu(x)
        elif activation == 'sigmoid':
            return self._sigmoid(x)
        elif activation == 'tanh':
            return self._tanh(x)
        elif activation == 'linear':
            return x
        elif activation == 'softmax':
            return self._softmax(x)
        else:
            raise ValueError(f"Unknown activation: {activation}")
    
    def _activation_derivative(self, x: np.ndarray, activation: str) -> np.ndarray:
        """Calculate activation derivative"""
        if activation == 'relu':
            return self._relu_derivative(x)
        elif activation == 'sigmoid':
            return self._sigmoid_derivative(x)
        elif activation == 'tanh':
            return self._tanh_derivative(x)
        elif activation == 'linear':
            return np.ones_like(x)
        else:
            raise ValueError(f"Derivative not implemented for: {activation}")
    
    def _forward_pass(self, X: np.ndarray) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Forward pass through the network
        
        Returns:
            Tuple of (activations, z_values) for each layer
        """
        activations = [X]
        z_values = []
        
        current_input = X
        
        for i, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            z = current_input @ weight + bias
            z_values.append(z)
            
            if i == len(self.weights) - 1:  # Output layer
                activation = self._activation_function(z, self.output_activation)
            else:  # Hidden layers
                activation = self._activation_function(z, self.activation)
            
            activations.append(activation)
            current_input = activation
        
        return activations, z_values
    
    def _backward_pass(
        self,
        X: np.ndarray,
        y: np.ndarray,
        activations: List[np.ndarray],
        z_values: List[np.ndarray]
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Backward pass (backpropagation)
        
        Returns:
            Tuple of (weight_gradients, bias_gradients)
        """
        m = X.shape[0]  # Number of samples
        
        weight_gradients = []
        bias_gradients = []
        
        # Output layer error
        if self.output_activation == 'softmax':
            # For softmax with cross-entropy loss
            delta = activations[-1] - y
        else:
            # For other activations with MSE loss
            output_error = activations[-1] - y
            if self.output_activation != 'linear':
                output_derivative = self._activation_derivative(z_values[-1], self.output_activation)
                delta = output_error * output_derivative
            else:
                delta = output_error
        
        # Propagate error backwards
        for i in range(len(self.weights) - 1, -1, -1):
            # Calculate gradients
            weight_gradient = activations[i].T @ delta / m
            bias_gradient = np.mean(delta, axis=0, keepdims=True)
            
            weight_gradients.insert(0, weight_gradient)
            bias_gradients.insert(0, bias_gradient)
            
            # Calculate error for previous layer
            if i > 0:
                delta = (delta @ self.weights[i].T) * self._activation_derivative(z_values[i-1], self.activation)
        
        return weight_gradients, bias_gradients
    
    def _calculate_loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate loss"""
        if self.output_activation == 'softmax':
            # Cross-entropy loss
            epsilon = 1e-15  # Prevent log(0)
            y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
            return -np.mean(np.sum(y_true * np.log(y_pred), axis=1))
        else:
            # Mean squared error
            return np.mean((y_true - y_pred) ** 2)
    
    def fit(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> 'NeuralNetwork':
        """
        Fit neural network
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples, n_outputs)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        if y.ndim == 1:
            if self.output_activation == 'softmax':
                # One-hot encode for multi-class classification
                n_classes = len(np.unique(y))
                y_encoded = np.zeros((len(y), n_classes))
                for i, cls in enumerate(np.unique(y)):
                    y_encoded[y == cls, i] = 1
                y = y_encoded
            else:
                y = y.reshape(-1, 1)
        
        n_samples, n_features = X.shape
        n_outputs = y.shape[1]
        
        # Initialize weights
        self._initialize_weights(n_features, n_outputs)
        
        self.loss_history = []
        
        # Training loop
        for iteration in range(self.max_iterations):
            if self.batch_size is None or self.batch_size >= n_samples:
                # Full batch gradient descent
                batch_X, batch_y = X, y
            else:
                # Mini-batch gradient descent
                batch_indices = np.random.choice(n_samples, self.batch_size, replace=False)
                batch_X, batch_y = X[batch_indices], y[batch_indices]
            
            # Forward pass
            activations, z_values = self._forward_pass(batch_X)
            
            # Calculate loss
            loss = self._calculate_loss(batch_y, activations[-1])
            self.loss_history.append(loss)
            
            # Backward pass
            weight_gradients, bias_gradients = self._backward_pass(batch_X, batch_y, activations, z_values)
            
            # Update weights and biases
            for i, (w_grad, b_grad) in enumerate(zip(weight_gradients, bias_gradients)):
                self.weights[i] -= self.learning_rate * w_grad
                self.biases[i] -= self.learning_rate * b_grad
            
            # Check for convergence
            if iteration > 0 and abs(self.loss_history[-2] - self.loss_history[-1]) < self.tolerance:
                break
        
        self.fitted = True
        return self
    
    def predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features to predict on (n_samples, n_features)
        
        Returns:
            Predictions (n_samples, n_outputs)
        """
        if not self.fitted:
            raise RuntimeError("Network must be fitted before making predictions")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        activations, _ = self._forward_pass(X)
        predictions = activations[-1]
        
        # For classification, return class predictions
        if self.output_activation == 'softmax':
            return np.argmax(predictions, axis=1)
        elif predictions.shape[1] == 1:
            return predictions.flatten()
        else:
            return predictions
    
    def predict_proba(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Predict class probabilities (for classification)
        
        Args:
            X: Features to predict on (n_samples, n_features)
        
        Returns:
            Class probabilities (n_samples, n_classes)
        """
        if not self.fitted:
            raise RuntimeError("Network must be fitted before making predictions")
        
        if self.output_activation not in ['sigmoid', 'softmax']:
            raise ValueError("predict_proba only available for classification tasks")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        activations, _ = self._forward_pass(X)
        return activations[-1]
    
    def score(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> float:
        """
        Calculate accuracy for classification or R² for regression
        
        Args:
            X: Features
            y: True targets
        
        Returns:
            Score
        """
        predictions = self.predict(X)
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        if self.output_activation == 'softmax' or (self.output_activation == 'sigmoid' and len(np.unique(y)) == 2):
            # Classification accuracy
            return np.mean(predictions == y)
        else:
            # Regression R²
            ss_res = np.sum((y - predictions) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0


class MLPClassifier(NeuralNetwork):
    """
    Multi-layer Perceptron Classifier
    
    Specialized neural network for classification tasks.
    """
    
    def __init__(
        self,
        hidden_layer_sizes: Tuple[int, ...] = (100,),
        activation: str = 'relu',
        learning_rate: float = 0.001,
        max_iter: int = 200,
        random_state: Optional[int] = None,
        batch_size: Optional[int] = 'auto'
    ):
        """
        Initialize MLP Classifier
        
        Args:
            hidden_layer_sizes: Sizes of hidden layers
            activation: Activation function
            learning_rate: Learning rate
            max_iter: Maximum iterations
            random_state: Random seed
            batch_size: Batch size ('auto' or int)
        """
        if batch_size == 'auto':
            batch_size = min(200, None)  # Will be set to None for small datasets
        
        super().__init__(
            hidden_layers=list(hidden_layer_sizes),
            activation=activation,
            output_activation='softmax',
            learning_rate=learning_rate,
            max_iterations=max_iter,
            random_state=random_state,
            batch_size=batch_size
        )


class MLPRegressor(NeuralNetwork):
    """
    Multi-layer Perceptron Regressor
    
    Specialized neural network for regression tasks.
    """
    
    def __init__(
        self,
        hidden_layer_sizes: Tuple[int, ...] = (100,),
        activation: str = 'relu',
        learning_rate: float = 0.001,
        max_iter: int = 200,
        random_state: Optional[int] = None,
        batch_size: Optional[int] = 'auto'
    ):
        """
        Initialize MLP Regressor
        
        Args:
            hidden_layer_sizes: Sizes of hidden layers
            activation: Activation function
            learning_rate: Learning rate
            max_iter: Maximum iterations
            random_state: Random seed
            batch_size: Batch size ('auto' or int)
        """
        if batch_size == 'auto':
            batch_size = min(200, None)  # Will be set to None for small datasets
        
        super().__init__(
            hidden_layers=list(hidden_layer_sizes),
            activation=activation,
            output_activation='linear',
            learning_rate=learning_rate,
            max_iterations=max_iter,
            random_state=random_state,
            batch_size=batch_size
        )


class Perceptron:
    """
    Simple Perceptron implementation
    
    Single layer perceptron for binary classification.
    """
    
    def __init__(self, learning_rate: float = 0.01, max_iter: int = 1000, random_state: Optional[int] = None):
        """
        Initialize Perceptron
        
        Args:
            learning_rate: Learning rate
            max_iter: Maximum iterations
            random_state: Random seed
        """
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.random_state = random_state
        
        self.weights = None
        self.bias = None
        self.fitted = False
        
        if self.random_state is not None:
            np.random.seed(self.random_state)
    
    def fit(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> 'Perceptron':
        """
        Fit perceptron
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,) - binary (0, 1) or (-1, 1)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        # Convert labels to -1, 1 format
        unique_labels = np.unique(y)
        if len(unique_labels) != 2:
            raise ValueError("Perceptron is for binary classification only")
        
        y_binary = np.where(y == unique_labels[0], -1, 1)
        
        n_samples, n_features = X.shape
        
        # Initialize weights and bias
        self.weights = np.random.normal(0, 0.01, n_features)
        self.bias = 0.0
        
        # Training loop
        for iteration in range(self.max_iter):
            errors = 0
            
            for i in range(n_samples):
                # Calculate prediction
                linear_output = np.dot(X[i], self.weights) + self.bias
                prediction = 1 if linear_output >= 0 else -1
                
                # Update weights if prediction is wrong
                if prediction != y_binary[i]:
                    self.weights += self.learning_rate * y_binary[i] * X[i]
                    self.bias += self.learning_rate * y_binary[i]
                    errors += 1
            
            # Stop if no errors
            if errors == 0:
                break
        
        self.fitted = True
        return self
    
    def predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features to predict on (n_samples, n_features)
        
        Returns:
            Binary predictions (n_samples,)
        """
        if not self.fitted:
            raise RuntimeError("Perceptron must be fitted before making predictions")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        linear_output = X @ self.weights + self.bias
        return (linear_output >= 0).astype(int)
    
    def score(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> float:
        """
        Calculate accuracy score
        
        Args:
            X: Features
            y: True targets
        
        Returns:
            Accuracy score
        """
        predictions = self.predict(X)
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        return np.mean(predictions == y)