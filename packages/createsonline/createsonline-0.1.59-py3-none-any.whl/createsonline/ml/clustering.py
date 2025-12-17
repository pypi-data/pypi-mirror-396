"""
CREATESONLINE Clustering Algorithms

Pure Python clustering implementations.
"""

import numpy as np
from typing import Optional, Union, List


class KMeans:
    """
    K-Means Clustering implementation
    
    Pure Python implementation with numpy for matrix operations.
    """
    
    def __init__(self, n_clusters: int = 8, max_iter: int = 300, tol: float = 1e-4, random_state: Optional[int] = None):
        """
        Initialize K-Means clustering
        
        Args:
            n_clusters: Number of clusters
            max_iter: Maximum number of iterations
            tol: Tolerance for convergence
            random_state: Random seed for reproducibility
        """
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        
        self.cluster_centers_ = None
        self.labels_ = None
        self.inertia_ = None
        self.n_iter_ = 0
        self.fitted = False
    
    def _init_centroids(self, X: np.ndarray) -> np.ndarray:
        """Initialize centroids randomly"""
        if self.random_state is not None:
            np.random.seed(self.random_state)
        
        n_samples, n_features = X.shape
        centroids = np.zeros((self.n_clusters, n_features))
        
        for i in range(self.n_clusters):
            # Choose random sample as initial centroid
            centroid_idx = np.random.randint(0, n_samples)
            centroids[i] = X[centroid_idx]
        
        return centroids
    
    def _assign_clusters(self, X: np.ndarray, centroids: np.ndarray) -> np.ndarray:
        """Assign each point to the nearest centroid"""
        n_samples = X.shape[0]
        labels = np.zeros(n_samples, dtype=int)
        
        for i, point in enumerate(X):
            distances = [np.linalg.norm(point - centroid) for centroid in centroids]
            labels[i] = np.argmin(distances)
        
        return labels
    
    def _update_centroids(self, X: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """Update centroids based on cluster assignments"""
        n_features = X.shape[1]
        centroids = np.zeros((self.n_clusters, n_features))
        
        for k in range(self.n_clusters):
            cluster_points = X[labels == k]
            if len(cluster_points) > 0:
                centroids[k] = np.mean(cluster_points, axis=0)
            else:
                # If cluster is empty, keep previous centroid
                centroids[k] = self.cluster_centers_[k] if self.cluster_centers_ is not None else np.zeros(n_features)
        
        return centroids
    
    def _calculate_inertia(self, X: np.ndarray, labels: np.ndarray, centroids: np.ndarray) -> float:
        """Calculate within-cluster sum of squares (inertia)"""
        inertia = 0.0
        for i, point in enumerate(X):
            centroid = centroids[labels[i]]
            inertia += np.sum((point - centroid) ** 2)
        return inertia
    
    def fit(self, X: Union[np.ndarray, list]) -> 'KMeans':
        """
        Fit K-Means clustering
        
        Args:
            X: Training data (n_samples, n_features)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        # Initialize centroids
        centroids = self._init_centroids(X)
        
        for iteration in range(self.max_iter):
            # Assign points to clusters
            labels = self._assign_clusters(X, centroids)
            
            # Update centroids
            new_centroids = self._update_centroids(X, labels)
            
            # Check for convergence
            centroid_shift = np.sum(np.linalg.norm(new_centroids - centroids, axis=1))
            if centroid_shift < self.tol:
                break
            
            centroids = new_centroids
            self.n_iter_ = iteration + 1
        
        self.cluster_centers_ = centroids
        self.labels_ = labels
        self.inertia_ = self._calculate_inertia(X, labels, centroids)
        self.fitted = True
        
        return self
    
    def predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Predict cluster labels for new data
        
        Args:
            X: Data to predict (n_samples, n_features)
        
        Returns:
            Cluster labels (n_samples,)
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before making predictions")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        return self._assign_clusters(X, self.cluster_centers_)
    
    def fit_predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Fit the model and predict cluster labels
        
        Args:
            X: Training data (n_samples, n_features)
        
        Returns:
            Cluster labels (n_samples,)
        """
        self.fit(X)
        return self.labels_
    
    def transform(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Transform data to cluster-distance space
        
        Args:
            X: Data to transform (n_samples, n_features)
        
        Returns:
            Distances to each cluster center (n_samples, n_clusters)
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before transforming")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        distances = np.zeros((X.shape[0], self.n_clusters))
        
        for i, point in enumerate(X):
            for j, centroid in enumerate(self.cluster_centers_):
                distances[i, j] = np.linalg.norm(point - centroid)
        
        return distances
    
    def score(self, X: Union[np.ndarray, list]) -> float:
        """
        Calculate the negative inertia (higher is better)
        
        Args:
            X: Data to score
        
        Returns:
            Negative inertia
        """
        labels = self.predict(X)
        inertia = self._calculate_inertia(np.array(X), labels, self.cluster_centers_)
        return -inertia


class DBScan:
    """
    DBSCAN (Density-Based Spatial Clustering) implementation
    
    Pure Python implementation for clustering based on density.
    """
    
    def __init__(self, eps: float = 0.5, min_samples: int = 5, metric: str = 'euclidean'):
        """
        Initialize DBSCAN clustering
        
        Args:
            eps: Maximum distance between two samples to be considered neighbors
            min_samples: Minimum number of samples in a neighborhood for a core point
            metric: Distance metric ('euclidean', 'manhattan')
        """
        self.eps = eps
        self.min_samples = min_samples
        self.metric = metric
        
        self.labels_ = None
        self.core_sample_indices_ = None
        self.fitted = False
    
    def _distance(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Calculate distance between two points"""
        if self.metric == 'euclidean':
            return np.linalg.norm(x1 - x2)
        elif self.metric == 'manhattan':
            return np.sum(np.abs(x1 - x2))
        else:
            raise ValueError(f"Unknown metric: {self.metric}")
    
    def _get_neighbors(self, X: np.ndarray, point_idx: int) -> List[int]:
        """Get all neighbors within eps distance"""
        neighbors = []
        point = X[point_idx]
        
        for i, other_point in enumerate(X):
            if self._distance(point, other_point) <= self.eps:
                neighbors.append(i)
        
        return neighbors
    
    def fit(self, X: Union[np.ndarray, list]) -> 'DBScan':
        """
        Fit DBSCAN clustering
        
        Args:
            X: Training data (n_samples, n_features)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples = X.shape[0]
        self.labels_ = np.full(n_samples, -1, dtype=int)  # -1 indicates noise
        cluster_id = 0
        
        visited = np.zeros(n_samples, dtype=bool)
        self.core_sample_indices_ = []
        
        for point_idx in range(n_samples):
            if visited[point_idx]:
                continue
            
            visited[point_idx] = True
            neighbors = self._get_neighbors(X, point_idx)
            
            if len(neighbors) < self.min_samples:
                # Point is noise (for now)
                continue
            
            # Point is a core point
            self.core_sample_indices_.append(point_idx)
            self.labels_[point_idx] = cluster_id
            
            # Expand cluster
            seed_set = neighbors.copy()
            i = 0
            while i < len(seed_set):
                neighbor_idx = seed_set[i]
                
                if not visited[neighbor_idx]:
                    visited[neighbor_idx] = True
                    neighbor_neighbors = self._get_neighbors(X, neighbor_idx)
                    
                    if len(neighbor_neighbors) >= self.min_samples:
                        # Neighbor is also a core point
                        self.core_sample_indices_.append(neighbor_idx)
                        seed_set.extend(neighbor_neighbors)
                
                if self.labels_[neighbor_idx] == -1:  # Not yet assigned to a cluster
                    self.labels_[neighbor_idx] = cluster_id
                
                i += 1
            
            cluster_id += 1
        
        self.core_sample_indices_ = np.array(self.core_sample_indices_)
        self.fitted = True
        return self
    
    def fit_predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Fit the model and return cluster labels
        
        Args:
            X: Training data (n_samples, n_features)
        
        Returns:
            Cluster labels (n_samples,) - -1 indicates noise
        """
        self.fit(X)
        return self.labels_


class AgglomerativeClustering:
    """
    Agglomerative (Hierarchical) Clustering implementation
    
    Pure Python implementation using linkage criteria.
    """
    
    def __init__(self, n_clusters: int = 2, linkage: str = 'ward', metric: str = 'euclidean'):
        """
        Initialize Agglomerative Clustering
        
        Args:
            n_clusters: Number of clusters to find
            linkage: Linkage criterion ('ward', 'complete', 'average', 'single')
            metric: Distance metric ('euclidean', 'manhattan')
        """
        self.n_clusters = n_clusters
        self.linkage = linkage
        self.metric = metric
        
        self.labels_ = None
        self.n_clusters_ = None
        self.fitted = False
    
    def _distance(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Calculate distance between two points"""
        if self.metric == 'euclidean':
            return np.linalg.norm(x1 - x2)
        elif self.metric == 'manhattan':
            return np.sum(np.abs(x1 - x2))
        else:
            raise ValueError(f"Unknown metric: {self.metric}")
    
    def _cluster_distance(self, cluster1: List[int], cluster2: List[int], X: np.ndarray) -> float:
        """Calculate distance between two clusters based on linkage criterion"""
        if self.linkage == 'single':
            # Minimum distance between any two points
            min_dist = float('inf')
            for i in cluster1:
                for j in cluster2:
                    dist = self._distance(X[i], X[j])
                    if dist < min_dist:
                        min_dist = dist
            return min_dist
        
        elif self.linkage == 'complete':
            # Maximum distance between any two points
            max_dist = 0.0
            for i in cluster1:
                for j in cluster2:
                    dist = self._distance(X[i], X[j])
                    if dist > max_dist:
                        max_dist = dist
            return max_dist
        
        elif self.linkage == 'average':
            # Average distance between all pairs of points
            total_dist = 0.0
            count = 0
            for i in cluster1:
                for j in cluster2:
                    total_dist += self._distance(X[i], X[j])
                    count += 1
            return total_dist / count if count > 0 else 0.0
        
        elif self.linkage == 'ward':
            # Ward linkage (minimum increase in within-cluster sum of squares)
            # Calculate centroids
            centroid1 = np.mean(X[cluster1], axis=0)
            centroid2 = np.mean(X[cluster2], axis=0)
            
            # Calculate merged centroid
            n1, n2 = len(cluster1), len(cluster2)
            merged_centroid = (n1 * centroid1 + n2 * centroid2) / (n1 + n2)
            
            # Calculate increase in sum of squares
            increase = 0.0
            for i in cluster1:
                increase += np.sum((X[i] - merged_centroid) ** 2) - np.sum((X[i] - centroid1) ** 2)
            for j in cluster2:
                increase += np.sum((X[j] - merged_centroid) ** 2) - np.sum((X[j] - centroid2) ** 2)
            
            return increase
        
        else:
            raise ValueError(f"Unknown linkage: {self.linkage}")
    
    def fit(self, X: Union[np.ndarray, list]) -> 'AgglomerativeClustering':
        """
        Fit Agglomerative Clustering
        
        Args:
            X: Training data (n_samples, n_features)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples = X.shape[0]
        
        # Initialize each point as its own cluster
        clusters = [[i] for i in range(n_samples)]
        
        # Merge clusters until we have the desired number
        while len(clusters) > self.n_clusters:
            min_dist = float('inf')
            merge_i, merge_j = -1, -1
            
            # Find the two closest clusters
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    dist = self._cluster_distance(clusters[i], clusters[j], X)
                    if dist < min_dist:
                        min_dist = dist
                        merge_i, merge_j = i, j
            
            # Merge the closest clusters
            if merge_i != -1 and merge_j != -1:
                clusters[merge_i].extend(clusters[merge_j])
                clusters.pop(merge_j)
        
        # Assign labels
        self.labels_ = np.zeros(n_samples, dtype=int)
        for cluster_id, cluster_points in enumerate(clusters):
            for point_idx in cluster_points:
                self.labels_[point_idx] = cluster_id
        
        self.n_clusters_ = len(clusters)
        self.fitted = True
        return self
    
    def fit_predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Fit the model and return cluster labels
        
        Args:
            X: Training data (n_samples, n_features)
        
        Returns:
            Cluster labels (n_samples,)
        """
        self.fit(X)
        return self.labels_


class GaussianMixture:
    """
    Gaussian Mixture Model implementation using Expectation-Maximization
    
    Pure Python implementation for probabilistic clustering.
    """
    
    def __init__(self, n_components: int = 1, max_iter: int = 100, tol: float = 1e-3, random_state: Optional[int] = None):
        """
        Initialize Gaussian Mixture Model
        
        Args:
            n_components: Number of mixture components
            max_iter: Maximum number of EM iterations
            tol: Tolerance for convergence
            random_state: Random seed for reproducibility
        """
        self.n_components = n_components
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        
        self.weights_ = None
        self.means_ = None
        self.covariances_ = None
        self.labels_ = None
        self.fitted = False
    
    def _initialize_parameters(self, X: np.ndarray):
        """Initialize GMM parameters"""
        if self.random_state is not None:
            np.random.seed(self.random_state)
        
        n_samples, n_features = X.shape
        
        # Initialize weights uniformly
        self.weights_ = np.ones(self.n_components) / self.n_components
        
        # Initialize means randomly
        self.means_ = np.zeros((self.n_components, n_features))
        for k in range(self.n_components):
            self.means_[k] = X[np.random.randint(0, n_samples)]
        
        # Initialize covariances as identity matrices
        self.covariances_ = np.array([np.eye(n_features) for _ in range(self.n_components)])
    
    def _multivariate_gaussian(self, X: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> np.ndarray:
        """Calculate multivariate Gaussian probability density"""
        n_features = X.shape[1]
        
        # Add small regularization to diagonal for numerical stability
        cov_reg = cov + 1e-6 * np.eye(n_features)
        
        try:
            cov_inv = np.linalg.inv(cov_reg)
            cov_det = np.linalg.det(cov_reg)
        except np.linalg.LinAlgError:
            # Fallback to regularized covariance
            cov_reg = np.eye(n_features)
            cov_inv = cov_reg
            cov_det = 1.0
        
        if cov_det <= 0:
            cov_det = 1e-6
        
        # Calculate probability density
        diff = X - mean
        exponent = -0.5 * np.sum((diff @ cov_inv) * diff, axis=1)
        
        normalization = 1.0 / np.sqrt((2 * np.pi) ** n_features * cov_det)
        
        return normalization * np.exp(exponent)
    
    def fit(self, X: Union[np.ndarray, list]) -> 'GaussianMixture':
        """
        Fit Gaussian Mixture Model using EM algorithm
        
        Args:
            X: Training data (n_samples, n_features)
        
        Returns:
            Self for method chaining
        """
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples, n_features = X.shape
        
        # Initialize parameters
        self._initialize_parameters(X)
        
        prev_log_likelihood = -np.inf
        
        for iteration in range(self.max_iter):
            # E-step: Calculate responsibilities
            responsibilities = np.zeros((n_samples, self.n_components))
            
            for k in range(self.n_components):
                responsibilities[:, k] = self.weights_[k] * self._multivariate_gaussian(
                    X, self.means_[k], self.covariances_[k]
                )
            
            # Normalize responsibilities
            total_responsibility = np.sum(responsibilities, axis=1, keepdims=True)
            total_responsibility[total_responsibility == 0] = 1e-15  # Avoid division by zero
            responsibilities /= total_responsibility
            
            # M-step: Update parameters
            N_k = np.sum(responsibilities, axis=0)
            
            # Update weights
            self.weights_ = N_k / n_samples
            
            # Update means
            for k in range(self.n_components):
                if N_k[k] > 0:
                    self.means_[k] = np.sum(responsibilities[:, k:k+1] * X, axis=0) / N_k[k]
            
            # Update covariances
            for k in range(self.n_components):
                if N_k[k] > 0:
                    diff = X - self.means_[k]
                    weighted_diff = responsibilities[:, k:k+1] * diff
                    self.covariances_[k] = (weighted_diff.T @ diff) / N_k[k]
                    
                    # Add regularization
                    self.covariances_[k] += 1e-6 * np.eye(n_features)
            
            # Check for convergence
            log_likelihood = np.sum(np.log(np.sum(responsibilities, axis=1) + 1e-15))
            
            if abs(log_likelihood - prev_log_likelihood) < self.tol:
                break
            
            prev_log_likelihood = log_likelihood
        
        # Assign labels based on highest responsibility
        self.labels_ = np.argmax(responsibilities, axis=1)
        self.fitted = True
        
        return self
    
    def predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Predict cluster labels for new data
        
        Args:
            X: Data to predict (n_samples, n_features)
        
        Returns:
            Cluster labels (n_samples,)
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before making predictions")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples = X.shape[0]
        responsibilities = np.zeros((n_samples, self.n_components))
        
        for k in range(self.n_components):
            responsibilities[:, k] = self.weights_[k] * self._multivariate_gaussian(
                X, self.means_[k], self.covariances_[k]
            )
        
        return np.argmax(responsibilities, axis=1)
    
    def predict_proba(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Predict cluster probabilities for new data
        
        Args:
            X: Data to predict (n_samples, n_features)
        
        Returns:
            Cluster probabilities (n_samples, n_components)
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before making predictions")
        
        X = np.array(X) if not isinstance(X, np.ndarray) else X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples = X.shape[0]
        responsibilities = np.zeros((n_samples, self.n_components))
        
        for k in range(self.n_components):
            responsibilities[:, k] = self.weights_[k] * self._multivariate_gaussian(
                X, self.means_[k], self.covariances_[k]
            )
        
        # Normalize
        total_responsibility = np.sum(responsibilities, axis=1, keepdims=True)
        total_responsibility[total_responsibility == 0] = 1e-15
        responsibilities /= total_responsibility
        
        return responsibilities
    
    def fit_predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Fit the model and return cluster labels
        
        Args:
            X: Training data (n_samples, n_features)
        
        Returns:
            Cluster labels (n_samples,)
        """
        self.fit(X)
        return self.labels_