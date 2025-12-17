"""
CREATESONLINE ML Metrics

Pure Python evaluation metrics.
"""

import numpy as np
from typing import Union, Dict, Any, List, Optional
import math


def accuracy_score(y_true: Union[np.ndarray, list], y_pred: Union[np.ndarray, list]) -> float:
    """
    Calculate accuracy score
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
    
    Returns:
        Accuracy score (0-1)
    """
    y_true = np.array(y_true) if not isinstance(y_true, np.ndarray) else y_true
    y_pred = np.array(y_pred) if not isinstance(y_pred, np.ndarray) else y_pred
    
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    return np.mean(y_true == y_pred)


def precision_score(
    y_true: Union[np.ndarray, list], 
    y_pred: Union[np.ndarray, list], 
    average: str = 'binary',
    pos_label: Union[str, int] = 1
) -> Union[float, np.ndarray]:
    """
    Calculate precision score
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        average: Averaging strategy ('binary', 'micro', 'macro', 'weighted', None)
        pos_label: Positive class label for binary classification
    
    Returns:
        Precision score(s)
    """
    y_true = np.array(y_true) if not isinstance(y_true, np.ndarray) else y_true
    y_pred = np.array(y_pred) if not isinstance(y_pred, np.ndarray) else y_pred
    
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    classes = np.unique(np.concatenate([y_true, y_pred]))
    
    if average == 'binary':
        if len(classes) > 2:
            raise ValueError("Binary classification requires exactly 2 classes")
        
        tp = np.sum((y_true == pos_label) & (y_pred == pos_label))
        fp = np.sum((y_true != pos_label) & (y_pred == pos_label))
        
        return tp / (tp + fp) if (tp + fp) > 0 else 0.0
    
    # Multi-class metrics
    precisions = []
    for cls in classes:
        tp = np.sum((y_true == cls) & (y_pred == cls))
        fp = np.sum((y_true != cls) & (y_pred == cls))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        precisions.append(precision)
    
    precisions = np.array(precisions)
    
    if average is None:
        return precisions
    elif average == 'macro':
        return np.mean(precisions)
    elif average == 'micro':
        tp_total = sum(np.sum((y_true == cls) & (y_pred == cls)) for cls in classes)
        fp_total = sum(np.sum((y_true != cls) & (y_pred == cls)) for cls in classes)
        return tp_total / (tp_total + fp_total) if (tp_total + fp_total) > 0 else 0.0
    elif average == 'weighted':
        weights = [np.sum(y_true == cls) for cls in classes]
        return np.average(precisions, weights=weights)
    else:
        raise ValueError(f"Unknown average: {average}")


def recall_score(
    y_true: Union[np.ndarray, list], 
    y_pred: Union[np.ndarray, list], 
    average: str = 'binary',
    pos_label: Union[str, int] = 1
) -> Union[float, np.ndarray]:
    """
    Calculate recall score
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        average: Averaging strategy ('binary', 'micro', 'macro', 'weighted', None)
        pos_label: Positive class label for binary classification
    
    Returns:
        Recall score(s)
    """
    y_true = np.array(y_true) if not isinstance(y_true, np.ndarray) else y_true
    y_pred = np.array(y_pred) if not isinstance(y_pred, np.ndarray) else y_pred
    
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    classes = np.unique(np.concatenate([y_true, y_pred]))
    
    if average == 'binary':
        if len(classes) > 2:
            raise ValueError("Binary classification requires exactly 2 classes")
        
        tp = np.sum((y_true == pos_label) & (y_pred == pos_label))
        fn = np.sum((y_true == pos_label) & (y_pred != pos_label))
        
        return tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    # Multi-class metrics
    recalls = []
    for cls in classes:
        tp = np.sum((y_true == cls) & (y_pred == cls))
        fn = np.sum((y_true == cls) & (y_pred != cls))
        
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        recalls.append(recall)
    
    recalls = np.array(recalls)
    
    if average is None:
        return recalls
    elif average == 'macro':
        return np.mean(recalls)
    elif average == 'micro':
        tp_total = sum(np.sum((y_true == cls) & (y_pred == cls)) for cls in classes)
        fn_total = sum(np.sum((y_true == cls) & (y_pred != cls)) for cls in classes)
        return tp_total / (tp_total + fn_total) if (tp_total + fn_total) > 0 else 0.0
    elif average == 'weighted':
        weights = [np.sum(y_true == cls) for cls in classes]
        return np.average(recalls, weights=weights)
    else:
        raise ValueError(f"Unknown average: {average}")


def f1_score(
    y_true: Union[np.ndarray, list], 
    y_pred: Union[np.ndarray, list], 
    average: str = 'binary',
    pos_label: Union[str, int] = 1
) -> Union[float, np.ndarray]:
    """
    Calculate F1 score (harmonic mean of precision and recall)
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        average: Averaging strategy ('binary', 'micro', 'macro', 'weighted', None)
        pos_label: Positive class label for binary classification
    
    Returns:
        F1 score(s)
    """
    precision = precision_score(y_true, y_pred, average=average, pos_label=pos_label)
    recall = recall_score(y_true, y_pred, average=average, pos_label=pos_label)
    
    if isinstance(precision, np.ndarray):
        # Handle array case
        f1_scores = np.zeros_like(precision)
        mask = (precision + recall) > 0
        f1_scores[mask] = 2 * precision[mask] * recall[mask] / (precision[mask] + recall[mask])
        return f1_scores
    else:
        # Handle scalar case
        return 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0


def confusion_matrix(y_true: Union[np.ndarray, list], y_pred: Union[np.ndarray, list]) -> np.ndarray:
    """
    Calculate confusion matrix
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
    
    Returns:
        Confusion matrix (n_classes, n_classes)
    """
    y_true = np.array(y_true) if not isinstance(y_true, np.ndarray) else y_true
    y_pred = np.array(y_pred) if not isinstance(y_pred, np.ndarray) else y_pred
    
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    classes = np.unique(np.concatenate([y_true, y_pred]))
    n_classes = len(classes)
    
    # Create class to index mapping
    class_to_idx = {cls: i for i, cls in enumerate(classes)}
    
    # Initialize confusion matrix
    cm = np.zeros((n_classes, n_classes), dtype=int)
    
    # Fill confusion matrix
    for true_label, pred_label in zip(y_true, y_pred):
        true_idx = class_to_idx[true_label]
        pred_idx = class_to_idx[pred_label]
        cm[true_idx, pred_idx] += 1
    
    return cm


def classification_report(
    y_true: Union[np.ndarray, list], 
    y_pred: Union[np.ndarray, list],
    target_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate classification report with precision, recall, F1-score for each class
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        target_names: Optional names for classes
    
    Returns:
        Classification report dictionary
    """
    y_true = np.array(y_true) if not isinstance(y_true, np.ndarray) else y_true
    y_pred = np.array(y_pred) if not isinstance(y_pred, np.ndarray) else y_pred
    
    classes = np.unique(np.concatenate([y_true, y_pred]))
    
    if target_names is None:
        target_names = [str(cls) for cls in classes]
    elif len(target_names) != len(classes):
        raise ValueError("target_names length must match number of classes")
    
    # Calculate metrics for each class
    precisions = precision_score(y_true, y_pred, average=None)
    recalls = recall_score(y_true, y_pred, average=None)
    f1_scores = f1_score(y_true, y_pred, average=None)
    
    # Calculate support (number of true instances for each class)
    supports = [np.sum(y_true == cls) for cls in classes]
    
    # Build report
    report = {}
    
    for i, (cls, name) in enumerate(zip(classes, target_names)):
        report[name] = {
            'precision': float(precisions[i]),
            'recall': float(recalls[i]),
            'f1-score': float(f1_scores[i]),
            'support': int(supports[i])
        }
    
    # Calculate macro averages
    report['macro avg'] = {
        'precision': float(np.mean(precisions)),
        'recall': float(np.mean(recalls)),
        'f1-score': float(np.mean(f1_scores)),
        'support': int(np.sum(supports))
    }
    
    # Calculate weighted averages
    weights = np.array(supports) / np.sum(supports)
    report['weighted avg'] = {
        'precision': float(np.average(precisions, weights=weights)),
        'recall': float(np.average(recalls, weights=weights)),
        'f1-score': float(np.average(f1_scores, weights=weights)),
        'support': int(np.sum(supports))
    }
    
    # Overall accuracy
    report['accuracy'] = float(accuracy_score(y_true, y_pred))
    
    return report


# Regression Metrics

def mean_squared_error(y_true: Union[np.ndarray, list], y_pred: Union[np.ndarray, list]) -> float:
    """
    Calculate Mean Squared Error
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        Mean squared error
    """
    y_true = np.array(y_true) if not isinstance(y_true, np.ndarray) else y_true
    y_pred = np.array(y_pred) if not isinstance(y_pred, np.ndarray) else y_pred
    
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    return np.mean((y_true - y_pred) ** 2)


def mean_absolute_error(y_true: Union[np.ndarray, list], y_pred: Union[np.ndarray, list]) -> float:
    """
    Calculate Mean Absolute Error
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        Mean absolute error
    """
    y_true = np.array(y_true) if not isinstance(y_true, np.ndarray) else y_true
    y_pred = np.array(y_pred) if not isinstance(y_pred, np.ndarray) else y_pred
    
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    return np.mean(np.abs(y_true - y_pred))


def root_mean_squared_error(y_true: Union[np.ndarray, list], y_pred: Union[np.ndarray, list]) -> float:
    """
    Calculate Root Mean Squared Error
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        Root mean squared error
    """
    return np.sqrt(mean_squared_error(y_true, y_pred))


def r2_score(y_true: Union[np.ndarray, list], y_pred: Union[np.ndarray, list]) -> float:
    """
    Calculate R-squared (coefficient of determination)
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        R-squared score
    """
    y_true = np.array(y_true) if not isinstance(y_true, np.ndarray) else y_true
    y_pred = np.array(y_pred) if not isinstance(y_pred, np.ndarray) else y_pred
    
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    
    return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0


def mean_absolute_percentage_error(y_true: Union[np.ndarray, list], y_pred: Union[np.ndarray, list]) -> float:
    """
    Calculate Mean Absolute Percentage Error
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        Mean absolute percentage error
    """
    y_true = np.array(y_true) if not isinstance(y_true, np.ndarray) else y_true
    y_pred = np.array(y_pred) if not isinstance(y_pred, np.ndarray) else y_pred
    
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    # Avoid division by zero
    mask = y_true != 0
    if not np.any(mask):
        return 0.0
    
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


# Clustering Metrics

def adjusted_rand_score(labels_true: Union[np.ndarray, list], labels_pred: Union[np.ndarray, list]) -> float:
    """
    Calculate Adjusted Rand Index for clustering evaluation
    
    Args:
        labels_true: True cluster labels
        labels_pred: Predicted cluster labels
    
    Returns:
        Adjusted Rand Index (-1 to 1, higher is better)
    """
    labels_true = np.array(labels_true) if not isinstance(labels_true, np.ndarray) else labels_true
    labels_pred = np.array(labels_pred) if not isinstance(labels_pred, np.ndarray) else labels_pred
    
    if len(labels_true) != len(labels_pred):
        raise ValueError("labels_true and labels_pred must have the same length")
    
    # Create contingency table
    classes_true = np.unique(labels_true)
    classes_pred = np.unique(labels_pred)
    
    contingency = np.zeros((len(classes_true), len(classes_pred)), dtype=int)
    
    for i, cls_true in enumerate(classes_true):
        for j, cls_pred in enumerate(classes_pred):
            contingency[i, j] = np.sum((labels_true == cls_true) & (labels_pred == cls_pred))
    
    # Calculate ARI
    n = len(labels_true)
    
    sum_comb_c = sum([math.comb(n_ij, 2) for n_ij in contingency.flatten() if n_ij >= 2])
    sum_comb_k = sum([math.comb(int(np.sum(contingency[i, :])), 2) for i in range(len(classes_true))])
    sum_comb_c_prime = sum([math.comb(int(np.sum(contingency[:, j])), 2) for j in range(len(classes_pred))])
    
    expected_index = sum_comb_k * sum_comb_c_prime / math.comb(n, 2) if n >= 2 else 0
    max_index = (sum_comb_k + sum_comb_c_prime) / 2
    
    if max_index == expected_index:
        return 1.0
    
    return (sum_comb_c - expected_index) / (max_index - expected_index)


def silhouette_score(X: Union[np.ndarray, list], labels: Union[np.ndarray, list], metric: str = 'euclidean') -> float:
    """
    Calculate Silhouette Score for clustering evaluation
    
    Args:
        X: Data points
        labels: Cluster labels
        metric: Distance metric ('euclidean', 'manhattan')
    
    Returns:
        Silhouette score (-1 to 1, higher is better)
    """
    X = np.array(X) if not isinstance(X, np.ndarray) else X
    labels = np.array(labels) if not isinstance(labels, np.ndarray) else labels
    
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    if len(X) != len(labels):
        raise ValueError("X and labels must have the same length")
    
    unique_labels = np.unique(labels)
    if len(unique_labels) <= 1:
        return 0.0
    
    def distance(x1, x2):
        if metric == 'euclidean':
            return np.linalg.norm(x1 - x2)
        elif metric == 'manhattan':
            return np.sum(np.abs(x1 - x2))
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    silhouette_scores = []
    
    for i, point in enumerate(X):
        own_cluster = labels[i]
        
        # Calculate a(i): average distance to points in same cluster
        same_cluster_points = X[labels == own_cluster]
        if len(same_cluster_points) > 1:
            a_i = np.mean([distance(point, other_point) for other_point in same_cluster_points if not np.array_equal(point, other_point)])
        else:
            a_i = 0.0
        
        # Calculate b(i): minimum average distance to points in other clusters
        b_i = float('inf')
        
        for other_cluster in unique_labels:
            if other_cluster != own_cluster:
                other_cluster_points = X[labels == other_cluster]
                if len(other_cluster_points) > 0:
                    avg_dist = np.mean([distance(point, other_point) for other_point in other_cluster_points])
                    b_i = min(b_i, avg_dist)
        
        # Calculate silhouette score for this point
        if b_i == float('inf'):
            s_i = 0.0
        else:
            s_i = (b_i - a_i) / max(a_i, b_i) if max(a_i, b_i) > 0 else 0.0
        
        silhouette_scores.append(s_i)
    
    return np.mean(silhouette_scores)


# Distance and Similarity Metrics

def euclidean_distance(x1: Union[np.ndarray, list], x2: Union[np.ndarray, list]) -> float:
    """Calculate Euclidean distance between two points"""
    x1 = np.array(x1) if not isinstance(x1, np.ndarray) else x1
    x2 = np.array(x2) if not isinstance(x2, np.ndarray) else x2
    
    return np.linalg.norm(x1 - x2)


def manhattan_distance(x1: Union[np.ndarray, list], x2: Union[np.ndarray, list]) -> float:
    """Calculate Manhattan distance between two points"""
    x1 = np.array(x1) if not isinstance(x1, np.ndarray) else x1
    x2 = np.array(x2) if not isinstance(x2, np.ndarray) else x2
    
    return np.sum(np.abs(x1 - x2))


def cosine_similarity(x1: Union[np.ndarray, list], x2: Union[np.ndarray, list]) -> float:
    """Calculate cosine similarity between two vectors"""
    x1 = np.array(x1) if not isinstance(x1, np.ndarray) else x1
    x2 = np.array(x2) if not isinstance(x2, np.ndarray) else x2
    
    dot_product = np.dot(x1, x2)
    norm_x1 = np.linalg.norm(x1)
    norm_x2 = np.linalg.norm(x2)
    
    if norm_x1 == 0 or norm_x2 == 0:
        return 0.0
    
    return dot_product / (norm_x1 * norm_x2)


def jaccard_similarity(set1: set, set2: set) -> float:
    """Calculate Jaccard similarity between two sets"""
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0