"""
CREATESONLINE Internal Machine Learning Module

Pure Python ML algorithms with zero external dependencies (except numpy).
Lightweight replacement for scikit-learn with AI-native features.
"""

from .regression import LinearRegression, LogisticRegression
from .classification import DecisionTreeClassifier, KNearestNeighbors
from .clustering import KMeans, DBScan
from .metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    confusion_matrix, classification_report
)
from .preprocessing import (
    StandardScaler, MinMaxScaler, LabelEncoder,
    train_test_split, cross_validate
)
from .neural import NeuralNetwork

__all__ = [
    # Regression
    'LinearRegression',
    'LogisticRegression',
    
    # Classification  
    'DecisionTreeClassifier',
    'KNearestNeighbors',
    
    # Clustering
    'KMeans',
    'DBScan',
    
    # Metrics
    'accuracy_score',
    'precision_score', 
    'recall_score',
    'f1_score',
    'mean_squared_error',
    'mean_absolute_error',
    'r2_score',
    'confusion_matrix',
    'classification_report',
    
    # Preprocessing
    'StandardScaler',
    'MinMaxScaler', 
    'LabelEncoder',
    'train_test_split',
    'cross_validate',
    
    # Neural Networks
    'NeuralNetwork'
]