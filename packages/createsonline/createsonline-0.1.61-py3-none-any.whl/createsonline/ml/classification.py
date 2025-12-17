"""
CREATESONLINE Classification Algorithms

Pure Python classification implementations.
"""

import numpy as np
from typing import Optional, Union, Any
from collections import Counter


class DecisionTreeClassifier:
    """
    Decision Tree Classifier implementation
    
    Pure Python implementation using information gain.
    """
    
    def __init__(self, max_depth: Optional[int] = None, min_samples_split: int = 2, min_samples_leaf: int = 1):
        """
        Initialize Decision Tree Classifier
        
        Args:
            max_depth: Maximum depth of the tree
            min_samples_split: Minimum samples required to split a node
            min_samples_leaf: Minimum samples required at a leaf node
        """
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        
        self.tree = None
        self.feature_importances_ = None
        self.fitted = False
    
    class Node:
        """Decision tree node"""
        def __init__(self):
            self.feature_index = None
            self.threshold = None
            self.left = None
            self.right = None
            self.value = None  # For leaf nodes
            self.samples = 0
            self.gini = 0.0
    
    def _gini_impurity(self, y: np.ndarray) -> float:
        """Calculate Gini impurity"""
        if len(y) == 0:
            return 0.0
        
        _, counts = np.unique(y, return_counts=True)
        probabilities = counts / len(y)
        return 1 - np.sum(probabilities ** 2)
    
    def _entropy(self, y: np.ndarray) -> float:
        """Calculate entropy"""
        if len(y) == 0:
            return 0.0
        
        _, counts = np.unique(y, return_counts=True)
        probabilities = counts / len(y)
        return -np.sum(probabilities * np.log2(probabilities + 1e-15))
    
    def _information_gain(self, y: np.ndarray, left_y: np.ndarray, right_y: np.ndarray) -> float:
        """Calculate information gain"""
        n = len(y)
        n_left, n_right = len(left_y), len(right_y)
        
        if n_left == 0 or n_right == 0:
            return 0.0
        
        entropy_parent = self._entropy(y)
        entropy_left = self._entropy(left_y)
        entropy_right = self._entropy(right_y)
        
        weighted_entropy = (n_left / n) * entropy_left + (n_right / n) * entropy_right
        return entropy_parent - weighted_entropy
    
    def _best_split(self, X: np.ndarray, y: np.ndarray) -> tuple:
        """Find the best split for the data"""
        best_gain = -1
        best_feature = None
        best_threshold = None
        
        n_features = X.shape[1]
        
        for feature_index in range(n_features):
            feature_values = X[:, feature_index]
            unique_values = np.unique(feature_values)
            
            for i in range(len(unique_values) - 1):
                threshold = (unique_values[i] + unique_values[i + 1]) / 2
                
                left_mask = feature_values <= threshold
                right_mask = ~left_mask
                
                if np.sum(left_mask) < self.min_samples_leaf or np.sum(right_mask) < self.min_samples_leaf:
                    continue
                
                left_y = y[left_mask]
                right_y = y[right_mask]
                
                gain = self._information_gain(y, left_y, right_y)
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature_index
                    best_threshold = threshold
        
        return best_feature, best_threshold, best_gain
    
    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int = 0) -> Node:
        """Recursively build the decision tree"""
        node = self.Node()
        node.samples = len(y)
        node.gini = self._gini_impurity(y)
        
        # Check stopping criteria
        if (self.max_depth is not None and depth >= self.max_depth) or \
           len(y) < self.min_samples_split or \
           len(np.unique(y)) == 1:
            # Leaf node
            node.value = Counter(y).most_common(1)[0][0]
            return node
        
        # Find best split
        feature_index, threshold, gain = self._best_split(X, y)
        
        if feature_index is None or gain <= 0:
            # Leaf node
            node.value = Counter(y).most_common(1)[0][0]
            return node
        
        # Split the data
        left_mask = X[:, feature_index] <= threshold
        right_mask = ~left_mask
        
        node.feature_index = feature_index
        node.threshold = threshold
        
        # Recursively build left and right subtrees
        node.left = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        node.right = self._build_tree(X[right_mask], y[right_mask], depth + 1)
        
        return node
    
    def fit(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> 'DecisionTreeClassifier':
        """
        Fit decision tree classifier
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        self.tree = self._build_tree(X, y)
        self.fitted = True
        return self
    
    def _predict_sample(self, sample: np.ndarray, node: Node) -> Any:
        """Predict a single sample"""
        if node.value is not None:  # Leaf node
            return node.value
        
        if sample[node.feature_index] <= node.threshold:
            return self._predict_sample(sample, node.left)
        else:
            return self._predict_sample(sample, node.right)
    
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
        
        predictions = []
        for sample in X:
            predictions.append(self._predict_sample(sample, self.tree))
        
        return np.array(predictions)
    
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


class KNearestNeighbors:
    """
    K-Nearest Neighbors Classifier implementation
    
    Pure Python implementation with different distance metrics.
    """
    
    def __init__(self, n_neighbors: int = 5, metric: str = 'euclidean', weights: str = 'uniform'):
        """
        Initialize KNN Classifier
        
        Args:
            n_neighbors: Number of neighbors to consider
            metric: Distance metric ('euclidean', 'manhattan', 'cosine')
            weights: Weight function ('uniform', 'distance')
        """
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.weights = weights
        
        self.X_train = None
        self.y_train = None
        self.fitted = False
    
    def _euclidean_distance(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Calculate Euclidean distance"""
        return np.sqrt(np.sum((x1 - x2) ** 2))
    
    def _manhattan_distance(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Calculate Manhattan distance"""
        return np.sum(np.abs(x1 - x2))
    
    def _cosine_distance(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Calculate Cosine distance"""
        dot_product = np.dot(x1, x2)
        norm_x1 = np.linalg.norm(x1)
        norm_x2 = np.linalg.norm(x2)
        
        if norm_x1 == 0 or norm_x2 == 0:
            return 1.0
        
        cosine_sim = dot_product / (norm_x1 * norm_x2)
        return 1 - cosine_sim
    
    def _distance(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Calculate distance based on metric"""
        if self.metric == 'euclidean':
            return self._euclidean_distance(x1, x2)
        elif self.metric == 'manhattan':
            return self._manhattan_distance(x1, x2)
        elif self.metric == 'cosine':
            return self._cosine_distance(x1, x2)
        else:
            raise ValueError(f"Unknown metric: {self.metric}")
    
    def fit(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> 'KNearestNeighbors':
        """
        Fit KNN classifier (just store training data)
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,)
        
        Returns:
            Self for method chaining
        """
        self.X_train = np.array(X) if not isinstance(X, np.ndarray) else X
        self.y_train = np.array(y) if not isinstance(y, np.ndarray) else y
        
        if self.X_train.ndim == 1:
            self.X_train = self.X_train.reshape(-1, 1)
        
        self.fitted = True
        return self
    
    def _predict_sample(self, sample: np.ndarray) -> Any:
        """Predict a single sample"""
        # Calculate distances to all training samples
        distances = []
        for i, train_sample in enumerate(self.X_train):
            dist = self._distance(sample, train_sample)
            distances.append((dist, self.y_train[i]))
        
        # Sort by distance and get k nearest neighbors
        distances.sort(key=lambda x: x[0])
        neighbors = distances[:self.n_neighbors]
        
        if self.weights == 'uniform':
            # Simple majority vote
            neighbor_labels = [label for _, label in neighbors]
            return Counter(neighbor_labels).most_common(1)[0][0]
        
        elif self.weights == 'distance':
            # Weight by inverse distance
            label_weights = {}
            for dist, label in neighbors:
                weight = 1 / (dist + 1e-15)  # Add small epsilon to avoid division by zero
                if label in label_weights:
                    label_weights[label] += weight
                else:
                    label_weights[label] = weight
            
            return max(label_weights.items(), key=lambda x: x[1])[0]
    
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
        
        predictions = []
        for sample in X:
            predictions.append(self._predict_sample(sample))
        
        return np.array(predictions)
    
    def predict_proba(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Predict class probabilities
        
        Args:
            X: Features to predict on (n_samples, n_features)
        
        Returns:
            Class probabilities (n_samples, n_classes)
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before making predictions")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        # Get unique classes
        unique_classes = np.unique(self.y_train)
        n_classes = len(unique_classes)
        class_to_index = {cls: i for i, cls in enumerate(unique_classes)}
        
        probabilities = []
        
        for sample in X:
            # Calculate distances to all training samples
            distances = []
            for i, train_sample in enumerate(self.X_train):
                dist = self._distance(sample, train_sample)
                distances.append((dist, self.y_train[i]))
            
            # Sort by distance and get k nearest neighbors
            distances.sort(key=lambda x: x[0])
            neighbors = distances[:self.n_neighbors]
            
            # Calculate class probabilities
            class_probs = np.zeros(n_classes)
            
            if self.weights == 'uniform':
                for _, label in neighbors:
                    class_probs[class_to_index[label]] += 1
                class_probs /= self.n_neighbors
            
            elif self.weights == 'distance':
                total_weight = 0
                for dist, label in neighbors:
                    weight = 1 / (dist + 1e-15)
                    class_probs[class_to_index[label]] += weight
                    total_weight += weight
                
                if total_weight > 0:
                    class_probs /= total_weight
            
            probabilities.append(class_probs)
        
        return np.array(probabilities)
    
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


class NaiveBayes:
    """
    Naive Bayes Classifier implementation
    
    Pure Python implementation for continuous features (Gaussian Naive Bayes).
    """
    
    def __init__(self):
        """Initialize Naive Bayes Classifier"""
        self.classes = None
        self.class_priors = {}
        self.feature_stats = {}  # {class: {feature_idx: {'mean': mean, 'var': var}}}
        self.fitted = False
    
    def fit(self, X: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> 'NaiveBayes':
        """
        Fit Naive Bayes classifier
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples, n_features = X.shape
        self.classes = np.unique(y)
        
        # Calculate class priors
        for cls in self.classes:
            self.class_priors[cls] = np.sum(y == cls) / n_samples
        
        # Calculate feature statistics for each class
        self.feature_stats = {}
        for cls in self.classes:
            self.feature_stats[cls] = {}
            class_samples = X[y == cls]
            
            for feature_idx in range(n_features):
                feature_values = class_samples[:, feature_idx]
                self.feature_stats[cls][feature_idx] = {
                    'mean': np.mean(feature_values),
                    'var': np.var(feature_values) + 1e-9  # Add small value to avoid division by zero
                }
        
        self.fitted = True
        return self
    
    def _gaussian_pdf(self, x: float, mean: float, var: float) -> float:
        """Calculate Gaussian probability density function"""
        return (1 / np.sqrt(2 * np.pi * var)) * np.exp(-0.5 * ((x - mean) ** 2) / var)
    
    def predict_proba(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Predict class probabilities
        
        Args:
            X: Features to predict on (n_samples, n_features)
        
        Returns:
            Class probabilities (n_samples, n_classes)
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before making predictions")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples, n_features = X.shape
        n_classes = len(self.classes)
        
        probabilities = np.zeros((n_samples, n_classes))
        
        for i, sample in enumerate(X):
            for j, cls in enumerate(self.classes):
                # Start with prior probability
                log_prob = np.log(self.class_priors[cls])
                
                # Multiply by feature likelihoods (in log space)
                for feature_idx in range(n_features):
                    feature_value = sample[feature_idx]
                    mean = self.feature_stats[cls][feature_idx]['mean']
                    var = self.feature_stats[cls][feature_idx]['var']
                    
                    likelihood = self._gaussian_pdf(feature_value, mean, var)
                    log_prob += np.log(likelihood + 1e-15)  # Add small value to avoid log(0)
                
                probabilities[i, j] = log_prob
        
        # Convert from log probabilities to probabilities
        # Use softmax to avoid numerical overflow
        probabilities = probabilities - np.max(probabilities, axis=1, keepdims=True)
        probabilities = np.exp(probabilities)
        probabilities = probabilities / np.sum(probabilities, axis=1, keepdims=True)
        
        return probabilities
    
    def predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features to predict on (n_samples, n_features)
        
        Returns:
            Predictions (n_samples,)
        """
        probabilities = self.predict_proba(X)
        class_indices = np.argmax(probabilities, axis=1)
        return self.classes[class_indices]
    
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