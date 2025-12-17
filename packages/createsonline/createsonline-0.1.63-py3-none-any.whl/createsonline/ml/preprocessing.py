"""
CREATESONLINE ML Preprocessing

Pure Python preprocessing utilities.
"""

import numpy as np
from typing import Union, List, Optional, Tuple, Dict
import random
import math


class StandardScaler:
    """
    Standardize features by removing mean and scaling to unit variance
    
    Pure Python implementation with numpy.
    """
    
    def __init__(self):
        """Initialize StandardScaler"""
        self.mean_ = None
        self.scale_ = None
        self.var_ = None
        self.fitted = False
    
    def fit(self, X: Union[np.ndarray, list]) -> 'StandardScaler':
        """
        Compute the mean and std to be used for later scaling
        
        Args:
            X: Training data (n_samples, n_features)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        self.mean_ = np.mean(X, axis=0)
        self.var_ = np.var(X, axis=0)
        self.scale_ = np.sqrt(self.var_)
        
        # Handle zero variance features
        self.scale_[self.scale_ == 0] = 1.0
        
        self.fitted = True
        return self
    
    def transform(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Standardize the data
        
        Args:
            X: Data to transform (n_samples, n_features)
        
        Returns:
            Transformed data
        """
        if not self.fitted:
            raise RuntimeError("Scaler must be fitted before transforming")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        return (X - self.mean_) / self.scale_
    
    def fit_transform(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Fit to data, then transform it
        
        Args:
            X: Data to fit and transform
        
        Returns:
            Transformed data
        """
        return self.fit(X).transform(X)
    
    def inverse_transform(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Scale back the data to the original representation
        
        Args:
            X: Transformed data
        
        Returns:
            Original scale data
        """
        if not self.fitted:
            raise RuntimeError("Scaler must be fitted before inverse transforming")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        return X * self.scale_ + self.mean_


class MinMaxScaler:
    """
    Scale features to a given range (default 0-1)
    
    Pure Python implementation with numpy.
    """
    
    def __init__(self, feature_range: Tuple[float, float] = (0, 1)):
        """
        Initialize MinMaxScaler
        
        Args:
            feature_range: Desired range of transformed data
        """
        self.feature_range = feature_range
        self.min_ = None
        self.scale_ = None
        self.data_min_ = None
        self.data_max_ = None
        self.data_range_ = None
        self.fitted = False
    
    def fit(self, X: Union[np.ndarray, list]) -> 'MinMaxScaler':
        """
        Compute the minimum and maximum to be used for later scaling
        
        Args:
            X: Training data (n_samples, n_features)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        self.data_min_ = np.min(X, axis=0)
        self.data_max_ = np.max(X, axis=0)
        self.data_range_ = self.data_max_ - self.data_min_
        
        # Handle constant features
        self.data_range_[self.data_range_ == 0] = 1.0
        
        feature_range_min, feature_range_max = self.feature_range
        self.scale_ = (feature_range_max - feature_range_min) / self.data_range_
        self.min_ = feature_range_min - self.data_min_ * self.scale_
        
        self.fitted = True
        return self
    
    def transform(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Scale the data to the specified range
        
        Args:
            X: Data to transform (n_samples, n_features)
        
        Returns:
            Transformed data
        """
        if not self.fitted:
            raise RuntimeError("Scaler must be fitted before transforming")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        return X * self.scale_ + self.min_
    
    def fit_transform(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Fit to data, then transform it
        
        Args:
            X: Data to fit and transform
        
        Returns:
            Transformed data
        """
        return self.fit(X).transform(X)
    
    def inverse_transform(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Undo the scaling of the data
        
        Args:
            X: Transformed data
        
        Returns:
            Original scale data
        """
        if not self.fitted:
            raise RuntimeError("Scaler must be fitted before inverse transforming")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        return (X - self.min_) / self.scale_


class LabelEncoder:
    """
    Encode categorical labels as integers
    
    Pure Python implementation.
    """
    
    def __init__(self):
        """Initialize LabelEncoder"""
        self.classes_ = None
        self.class_to_index_ = None
        self.fitted = False
    
    def fit(self, y: Union[np.ndarray, list]) -> 'LabelEncoder':
        """
        Fit label encoder
        
        Args:
            y: Target values
        
        Returns:
            Self for method chaining
        """
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        self.classes_ = np.unique(y)
        self.class_to_index_ = {cls: i for i, cls in enumerate(self.classes_)}
        
        self.fitted = True
        return self
    
    def transform(self, y: Union[np.ndarray, list]) -> np.ndarray:
        """
        Transform labels to normalized encoding
        
        Args:
            y: Target values
        
        Returns:
            Encoded labels
        """
        if not self.fitted:
            raise RuntimeError("LabelEncoder must be fitted before transforming")
        
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        encoded = np.zeros(len(y), dtype=int)
        for i, label in enumerate(y):
            if label in self.class_to_index_:
                encoded[i] = self.class_to_index_[label]
            else:
                raise ValueError(f"Unseen label: {label}")
        
        return encoded
    
    def fit_transform(self, y: Union[np.ndarray, list]) -> np.ndarray:
        """
        Fit label encoder and return encoded labels
        
        Args:
            y: Target values
        
        Returns:
            Encoded labels
        """
        return self.fit(y).transform(y)
    
    def inverse_transform(self, y: Union[np.ndarray, list]) -> np.ndarray:
        """
        Transform labels back to original encoding
        
        Args:
            y: Encoded labels
        
        Returns:
            Original labels
        """
        if not self.fitted:
            raise RuntimeError("LabelEncoder must be fitted before inverse transforming")
        
        y = np.array(y) if not isinstance(y, np.ndarray) else y
        
        original = np.zeros(len(y), dtype=object)
        for i, encoded_label in enumerate(y):
            if 0 <= encoded_label < len(self.classes_):
                original[i] = self.classes_[encoded_label]
            else:
                raise ValueError(f"Invalid encoded label: {encoded_label}")
        
        return original


class OneHotEncoder:
    """
    Encode categorical features as one-hot numeric array
    
    Pure Python implementation.
    """
    
    def __init__(self, drop_first: bool = False):
        """
        Initialize OneHotEncoder
        
        Args:
            drop_first: Whether to drop the first category to avoid multicollinearity
        """
        self.drop_first = drop_first
        self.categories_ = None
        self.n_features_out_ = None
        self.fitted = False
    
    def fit(self, X: Union[np.ndarray, list]) -> 'OneHotEncoder':
        """
        Fit OneHotEncoder to X
        
        Args:
            X: Categorical data (n_samples, n_features)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_features = X.shape[1]
        self.categories_ = []
        
        for feature_idx in range(n_features):
            unique_categories = np.unique(X[:, feature_idx])
            self.categories_.append(unique_categories)
        
        # Calculate output size
        self.n_features_out_ = sum(
            len(cats) - (1 if self.drop_first else 0) 
            for cats in self.categories_
        )
        
        self.fitted = True
        return self
    
    def transform(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Transform X using one-hot encoding
        
        Args:
            X: Categorical data (n_samples, n_features)
        
        Returns:
            One-hot encoded data
        """
        if not self.fitted:
            raise RuntimeError("OneHotEncoder must be fitted before transforming")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples, n_features = X.shape
        encoded = np.zeros((n_samples, self.n_features_out_))
        
        col_idx = 0
        for feature_idx in range(n_features):
            categories = self.categories_[feature_idx]
            start_idx = 1 if self.drop_first else 0
            
            for cat_idx in range(start_idx, len(categories)):
                category = categories[cat_idx]
                mask = X[:, feature_idx] == category
                encoded[mask, col_idx] = 1
                col_idx += 1
        
        return encoded
    
    def fit_transform(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Fit OneHotEncoder to X, then transform X
        
        Args:
            X: Categorical data
        
        Returns:
            One-hot encoded data
        """
        return self.fit(X).transform(X)


class PolynomialFeatures:
    """
    Generate polynomial and interaction features
    
    Pure Python implementation.
    """
    
    def __init__(self, degree: int = 2, include_bias: bool = True, interaction_only: bool = False):
        """
        Initialize PolynomialFeatures
        
        Args:
            degree: Maximum degree of polynomial features
            include_bias: Whether to include bias column (all ones)
            interaction_only: Whether to produce interaction features only
        """
        self.degree = degree
        self.include_bias = include_bias
        self.interaction_only = interaction_only
        self.n_input_features_ = None
        self.n_output_features_ = None
        self.fitted = False
    
    def fit(self, X: Union[np.ndarray, list]) -> 'PolynomialFeatures':
        """
        Compute number of output features
        
        Args:
            X: Input data (n_samples, n_features)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        self.n_input_features_ = X.shape[1]
        
        # Calculate number of output features
        if self.interaction_only:
            # Only interaction terms
            self.n_output_features_ = 1  # bias
            for d in range(2, self.degree + 1):
                self.n_output_features_ += math.comb(self.n_input_features_, d)
            if not self.include_bias:
                self.n_output_features_ -= 1
        else:
            # All polynomial terms
            self.n_output_features_ = math.comb(self.n_input_features_ + self.degree, self.degree)
            if not self.include_bias:
                self.n_output_features_ -= 1
        
        self.fitted = True
        return self
    
    def transform(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Transform data to polynomial features
        
        Args:
            X: Input data (n_samples, n_features)
        
        Returns:
            Polynomial features
        """
        if not self.fitted:
            raise RuntimeError("PolynomialFeatures must be fitted before transforming")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples, n_features = X.shape
        
        # For simplicity, implement basic polynomial features
        # This is a simplified version - full implementation would handle all combinations
        features = []
        
        if self.include_bias:
            features.append(np.ones(n_samples))
        
        # Original features
        if not self.interaction_only:
            for i in range(n_features):
                features.append(X[:, i])
        
        # Polynomial features
        for degree in range(2, self.degree + 1):
            if self.interaction_only:
                # Only cross terms
                for i in range(n_features):
                    for j in range(i + 1, n_features):
                        features.append(X[:, i] * X[:, j])
            else:
                # All polynomial terms
                for i in range(n_features):
                    features.append(X[:, i] ** degree)
                
                # Cross terms
                if degree == 2:  # Only implement degree 2 cross terms for simplicity
                    for i in range(n_features):
                        for j in range(i + 1, n_features):
                            features.append(X[:, i] * X[:, j])
        
        return np.column_stack(features)
    
    def fit_transform(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Fit to data, then transform it
        
        Args:
            X: Input data
        
        Returns:
            Polynomial features
        """
        return self.fit(X).transform(X)


# Data splitting functions

def train_test_split(
    *arrays,
    test_size: Union[float, int] = 0.25,
    train_size: Optional[Union[float, int]] = None,
    random_state: Optional[int] = None,
    shuffle: bool = True,
    stratify: Optional[Union[np.ndarray, list]] = None
) -> List[np.ndarray]:
    """
    Split arrays into random train and test subsets
    
    Args:
        *arrays: Sequence of indexables with same length
        test_size: Proportion or absolute number of test samples
        train_size: Proportion or absolute number of train samples
        random_state: Random seed for reproducibility
        shuffle: Whether to shuffle data before splitting
        stratify: Array for stratified splitting
    
    Returns:
        List of train-test splits of inputs
    """
    if len(arrays) == 0:
        raise ValueError("At least one array required as input")
    
    # Convert to numpy arrays
    arrays = [np.array(arr) if not isinstance(arr, np.ndarray) else arr for arr in arrays]
    
    # Check that all arrays have the same length
    n_samples = len(arrays[0])
    for arr in arrays[1:]:
        if len(arr) != n_samples:
            raise ValueError("All arrays must have the same length")
    
    if random_state is not None:
        random.seed(random_state)
        np.random.seed(random_state)
    
    # Calculate split sizes
    if isinstance(test_size, float):
        test_size = int(n_samples * test_size)
    
    if train_size is not None:
        if isinstance(train_size, float):
            train_size = int(n_samples * train_size)
        if train_size + test_size > n_samples:
            raise ValueError("train_size + test_size exceeds total samples")
    else:
        train_size = n_samples - test_size
    
    # Create indices
    indices = list(range(n_samples))
    
    if stratify is not None:
        # Stratified split
        stratify = np.array(stratify) if not isinstance(stratify, np.ndarray) else stratify
        unique_classes = np.unique(stratify)
        
        train_indices = []
        test_indices = []
        
        for cls in unique_classes:
            cls_indices = [i for i in indices if stratify[i] == cls]
            if shuffle:
                random.shuffle(cls_indices)
            
            cls_test_size = int(len(cls_indices) * (test_size / n_samples))
            cls_train_size = len(cls_indices) - cls_test_size
            
            test_indices.extend(cls_indices[:cls_test_size])
            train_indices.extend(cls_indices[cls_test_size:cls_test_size + cls_train_size])
        
        if shuffle:
            random.shuffle(train_indices)
            random.shuffle(test_indices)
    
    else:
        # Regular split
        if shuffle:
            random.shuffle(indices)
        
        test_indices = indices[:test_size]
        train_indices = indices[test_size:test_size + train_size]
    
    # Split arrays
    result = []
    for arr in arrays:
        train_arr = arr[train_indices]
        test_arr = arr[test_indices]
        result.extend([train_arr, test_arr])
    
    return result


def cross_validate(
    estimator,
    X: Union[np.ndarray, list],
    y: Union[np.ndarray, list],
    cv: int = 5,
    scoring: str = 'accuracy',
    random_state: Optional[int] = None
) -> Dict[str, np.ndarray]:
    """
    Evaluate metric(s) by cross-validation
    
    Args:
        estimator: ML estimator object
        X: Features
        y: Target
        cv: Number of folds
        scoring: Scoring metric ('accuracy', 'precision', 'recall', 'f1', 'mse', 'r2')
        random_state: Random seed for reproducibility
    
    Returns:
        Dictionary with test scores
    """
    X = np.array(X) if not isinstance(X, np.ndarray) else X
    y = np.array(y) if not isinstance(y, np.ndarray) else y
    
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    n_samples = len(X)
    if n_samples != len(y):
        raise ValueError("X and y must have the same length")
    
    if random_state is not None:
        random.seed(random_state)
    
    # Create folds
    indices = list(range(n_samples))
    random.shuffle(indices)
    
    fold_size = n_samples // cv
    folds = []
    
    for i in range(cv):
        start = i * fold_size
        end = start + fold_size if i < cv - 1 else n_samples
        test_indices = indices[start:end]
        train_indices = [idx for idx in indices if idx not in test_indices]
        folds.append((train_indices, test_indices))
    
    # Evaluate each fold
    scores = []
    
    for train_indices, test_indices in folds:
        X_train, X_test = X[train_indices], X[test_indices]
        y_train, y_test = y[train_indices], y[test_indices]
        
        # Clone estimator (simple copy for basic estimators)
        fold_estimator = type(estimator)(**estimator.__dict__)
        
        # Fit and predict
        fold_estimator.fit(X_train, y_train)
        y_pred = fold_estimator.predict(X_test)
        
        # Calculate score
        if scoring == 'accuracy':
            from .metrics import accuracy_score
            score = accuracy_score(y_test, y_pred)
        elif scoring == 'precision':
            from .metrics import precision_score
            score = precision_score(y_test, y_pred, average='weighted')
        elif scoring == 'recall':
            from .metrics import recall_score
            score = recall_score(y_test, y_pred, average='weighted')
        elif scoring == 'f1':
            from .metrics import f1_score
            score = f1_score(y_test, y_pred, average='weighted')
        elif scoring == 'mse':
            from .metrics import mean_squared_error
            score = mean_squared_error(y_test, y_pred)
        elif scoring == 'r2':
            from .metrics import r2_score
            score = r2_score(y_test, y_pred)
        else:
            raise ValueError(f"Unknown scoring: {scoring}")
        
        scores.append(score)
    
    return {'test_score': np.array(scores)}


# Feature selection utilities

def select_k_best_features(
    X: Union[np.ndarray, list],
    y: Union[np.ndarray, list],
    k: int = 10,
    score_func: str = 'f_classif'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Select k best features based on statistical tests
    
    Args:
        X: Features
        y: Target
        k: Number of features to select
        score_func: Scoring function ('f_classif', 'mutual_info')
    
    Returns:
        Tuple of (selected_features, feature_indices)
    """
    X = np.array(X) if not isinstance(X, np.ndarray) else X
    y = np.array(y) if not isinstance(y, np.ndarray) else y
    
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    n_features = X.shape[1]
    k = min(k, n_features)
    
    if score_func == 'f_classif':
        # Simple F-test for classification
        scores = []
        for feature_idx in range(n_features):
            feature = X[:, feature_idx]
            
            # Calculate F-statistic (simplified)
            classes = np.unique(y)
            between_class_var = 0
            within_class_var = 0
            overall_mean = np.mean(feature)
            
            for cls in classes:
                class_data = feature[y == cls]
                class_mean = np.mean(class_data)
                class_size = len(class_data)
                
                between_class_var += class_size * (class_mean - overall_mean) ** 2
                within_class_var += np.sum((class_data - class_mean) ** 2)
            
            between_class_var /= (len(classes) - 1)
            within_class_var /= (len(y) - len(classes))
            
            f_stat = between_class_var / within_class_var if within_class_var > 0 else 0
            scores.append(f_stat)
    
    elif score_func == 'mutual_info':
        # Simplified mutual information
        scores = []
        for feature_idx in range(n_features):
            feature = X[:, feature_idx]
            
            # Discretize continuous features (simple binning)
            if len(np.unique(feature)) > 10:  # Assume continuous
                bins = np.linspace(np.min(feature), np.max(feature), 5)
                feature_binned = np.digitize(feature, bins)
            else:
                feature_binned = feature
            
            # Calculate mutual information (simplified)
            mi = 0.0
            for f_val in np.unique(feature_binned):
                for y_val in np.unique(y):
                    p_xy = np.mean((feature_binned == f_val) & (y == y_val))
                    p_x = np.mean(feature_binned == f_val)
                    p_y = np.mean(y == y_val)
                    
                    if p_xy > 0 and p_x > 0 and p_y > 0:
                        mi += p_xy * np.log(p_xy / (p_x * p_y))
            
            scores.append(mi)
    
    else:
        raise ValueError(f"Unknown score_func: {score_func}")
    
    # Select k best features
    feature_indices = np.argsort(scores)[-k:]
    selected_features = X[:, feature_indices]
    
    return selected_features, feature_indices