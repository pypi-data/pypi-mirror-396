"""
Synthetic Datasets for Testing Oblique Decision Trees

This module provides synthetic datasets specifically designed to test
oblique decision tree algorithms. These datasets feature decision boundaries
that are not axis-parallel, making them ideal for evaluating the advantage
of oblique splits over axis-parallel splits.

Key Datasets:
- make_oblique_classification: General oblique boundary with noise
- make_xor_dataset: Classic XOR problem (non-linearly separable)
- make_diagonal_dataset: 45-degree diagonal boundary
- make_multiclass_oblique: Multi-class oblique boundaries
- make_nested_rectangles: Nested rectangles (needs oblique cuts)
"""

from typing import Tuple, Optional
import numpy as np


def make_oblique_classification(
    n_samples: int = 100,
    n_features: int = 2,
    angle: float = 45.0,
    noise: float = 0.1,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a 2-class classification dataset with an oblique decision boundary.
    
    Creates a dataset where the optimal decision boundary is a hyperplane
    at the specified angle from the horizontal axis.
    
    Args:
        n_samples: Total number of samples.
        n_features: Number of features (first 2 determine boundary, rest are noise).
        angle: Angle of the decision boundary in degrees (0 = horizontal, 90 = vertical).
        noise: Standard deviation of Gaussian noise added to samples.
        random_state: Random seed for reproducibility.
    
    Returns:
        Tuple of (X, y) where:
            - X: Feature matrix of shape (n_samples, n_features)
            - y: Class labels of shape (n_samples,) with values 0 or 1
    
    Example:
        >>> X, y = make_oblique_classification(n_samples=100, angle=45)
        >>> X.shape
        (100, 2)
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    # Generate random points in [0, 1]^n_features
    X = np.random.randn(n_samples, n_features)
    
    # Convert angle to radians
    theta = np.radians(angle)
    
    # Decision boundary: a*x + b*y = c
    # For angle theta: cos(theta)*x + sin(theta)*y = 0
    a = np.cos(theta)
    b = np.sin(theta)
    
    # Compute decision value
    decision = a * X[:, 0] + b * X[:, 1]
    
    # Add noise
    if noise > 0:
        decision += np.random.randn(n_samples) * noise
    
    # Assign classes based on sign
    y = (decision > 0).astype(int)
    
    return X, y


def make_xor_dataset(
    n_samples: int = 200,
    noise: float = 0.05,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate an XOR (exclusive or) classification dataset.
    
    The XOR problem is a classic non-linearly separable dataset that requires
    at least two decision boundaries to separate. This is useful for testing
    that oblique trees can build multi-level structures.
    
    Distribution:
        - Class 0: (low, low) and (high, high) quadrants
        - Class 1: (low, high) and (high, low) quadrants
    
    Args:
        n_samples: Total number of samples (divided among 4 quadrants).
        noise: Standard deviation of Gaussian noise.
        random_state: Random seed for reproducibility.
    
    Returns:
        Tuple of (X, y) where X is (n_samples, 2) and y is (n_samples,).
    
    Example:
        >>> X, y = make_xor_dataset(n_samples=200)
        >>> # Requires multiple splits to separate
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    n_per_quadrant = n_samples // 4
    
    # Generate points for each quadrant
    # Class 0: (low, low) centered at (0, 0)
    X_00 = np.random.randn(n_per_quadrant, 2) * 0.3 + np.array([0, 0])
    y_00 = np.zeros(n_per_quadrant, dtype=int)
    
    # Class 0: (high, high) centered at (1, 1)
    X_11 = np.random.randn(n_per_quadrant, 2) * 0.3 + np.array([1, 1])
    y_11 = np.zeros(n_per_quadrant, dtype=int)
    
    # Class 1: (low, high) centered at (0, 1)
    X_01 = np.random.randn(n_per_quadrant, 2) * 0.3 + np.array([0, 1])
    y_01 = np.ones(n_per_quadrant, dtype=int)
    
    # Class 1: (high, low) centered at (1, 0)
    X_10 = np.random.randn(n_per_quadrant, 2) * 0.3 + np.array([1, 0])
    y_10 = np.ones(n_per_quadrant, dtype=int)
    
    # Combine
    X = np.vstack([X_00, X_11, X_01, X_10])
    y = np.concatenate([y_00, y_11, y_01, y_10])
    
    # Add noise
    if noise > 0:
        X += np.random.randn(*X.shape) * noise
    
    # Shuffle
    indices = np.random.permutation(len(y))
    return X[indices], y[indices]


def make_diagonal_dataset(
    n_samples: int = 100,
    margin: float = 0.2,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a dataset with a clear 45-degree diagonal decision boundary.
    
    Creates a perfectly separable dataset where the optimal split is
    along the line x + y = 1 (45-degree diagonal).
    
    This is ideal for testing that oblique trees find diagonal splits
    while axis-parallel trees would need multiple splits.
    
    Args:
        n_samples: Total number of samples.
        margin: Separation margin between classes.
        random_state: Random seed for reproducibility.
    
    Returns:
        Tuple of (X, y) where X is (n_samples, 2) and y is (n_samples,).
    
    Example:
        >>> X, y = make_diagonal_dataset(n_samples=100)
        >>> # Optimal split: x + y - 1 = 0
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    n_per_class = n_samples // 2
    
    # Class 0: below diagonal x + y < 1 - margin
    X_0 = np.random.rand(n_per_class, 2) * 0.8
    X_0 = X_0[X_0[:, 0] + X_0[:, 1] < (1 - margin)]
    while len(X_0) < n_per_class:
        extra = np.random.rand(n_per_class, 2) * 0.8
        extra = extra[extra[:, 0] + extra[:, 1] < (1 - margin)]
        X_0 = np.vstack([X_0, extra])
    X_0 = X_0[:n_per_class]
    y_0 = np.zeros(n_per_class, dtype=int)
    
    # Class 1: above diagonal x + y > 1 + margin
    X_1 = np.random.rand(n_per_class, 2) * 0.8 + 0.2
    X_1 = X_1[X_1[:, 0] + X_1[:, 1] > (1 + margin)]
    while len(X_1) < n_per_class:
        extra = np.random.rand(n_per_class, 2) * 0.8 + 0.2
        extra = extra[extra[:, 0] + extra[:, 1] > (1 + margin)]
        X_1 = np.vstack([X_1, extra])
    X_1 = X_1[:n_per_class]
    y_1 = np.ones(n_per_class, dtype=int)
    
    # Combine and shuffle
    X = np.vstack([X_0, X_1])
    y = np.concatenate([y_0, y_1])
    
    indices = np.random.permutation(len(y))
    return X[indices], y[indices]


def make_multiclass_oblique(
    n_samples: int = 150,
    n_classes: int = 3,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a multi-class dataset with oblique decision boundaries.
    
    Creates a dataset with n_classes classes arranged in sectors,
    requiring oblique (radial) decision boundaries to separate them.
    
    This tests multi-class support and the ability to find different
    oblique splits at different levels of the tree.
    
    Args:
        n_samples: Total number of samples (divided among classes).
        n_classes: Number of classes (3 or more recommended).
        random_state: Random seed for reproducibility.
    
    Returns:
        Tuple of (X, y) where X is (n_samples, 2) and y has n_classes values.
    
    Example:
        >>> X, y = make_multiclass_oblique(n_samples=150, n_classes=3)
        >>> len(np.unique(y))
        3
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    n_per_class = n_samples // n_classes
    
    X_list = []
    y_list = []
    
    for cls in range(n_classes):
        # Angle for this class sector
        angle_start = cls * (2 * np.pi / n_classes)
        angle_end = (cls + 1) * (2 * np.pi / n_classes)
        
        # Generate points in this sector
        angles = np.random.uniform(angle_start, angle_end, n_per_class)
        radii = np.random.uniform(0.2, 1.0, n_per_class)
        
        X_cls = np.column_stack([
            radii * np.cos(angles),
            radii * np.sin(angles)
        ])
        
        X_list.append(X_cls)
        y_list.append(np.full(n_per_class, cls, dtype=int))
    
    X = np.vstack(X_list)
    y = np.concatenate(y_list)
    
    # Shuffle
    indices = np.random.permutation(len(y))
    return X[indices], y[indices]


def make_nested_rectangles(
    n_samples: int = 200,
    n_rectangles: int = 2,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate nested rectangles dataset.
    
    Creates alternating classes in concentric rectangles. This dataset
    benefits from oblique splits at corners to reduce tree complexity.
    
    Args:
        n_samples: Total number of samples.
        n_rectangles: Number of nested rectangles.
        random_state: Random seed for reproducibility.
    
    Returns:
        Tuple of (X, y) where X is (n_samples, 2) and y is (n_samples,).
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    n_per_rect = n_samples // n_rectangles
    
    X_list = []
    y_list = []
    
    for i in range(n_rectangles):
        # Inner and outer bounds for this rectangle
        inner = i / n_rectangles
        outer = (i + 1) / n_rectangles
        
        # Generate points in this ring
        X_rect = []
        while len(X_rect) < n_per_rect:
            candidates = np.random.uniform(0, 1, (n_per_rect * 2, 2))
            # Check if in the ring (between inner and outer bounds)
            max_abs = np.maximum(np.abs(candidates[:, 0] - 0.5), 
                                  np.abs(candidates[:, 1] - 0.5))
            in_ring = (max_abs >= inner / 2) & (max_abs < outer / 2)
            X_rect.extend(candidates[in_ring].tolist())
        
        X_rect = np.array(X_rect[:n_per_rect])
        X_list.append(X_rect)
        y_list.append(np.full(n_per_rect, i % 2, dtype=int))  # Alternating classes
    
    X = np.vstack(X_list)
    y = np.concatenate(y_list)
    
    # Shuffle
    indices = np.random.permutation(len(y))
    return X[indices], y[indices]


def make_3d_oblique(
    n_samples: int = 200,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a 3D dataset with an oblique decision boundary.
    
    Creates a dataset where the optimal split is a plane at an angle
    to all three axes: x + y + z = constant.
    
    Args:
        n_samples: Total number of samples.
        random_state: Random seed for reproducibility.
    
    Returns:
        Tuple of (X, y) where X is (n_samples, 3) and y is (n_samples,).
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    X = np.random.randn(n_samples, 3)
    
    # Decision boundary: x + y + z = 0
    decision = X[:, 0] + X[:, 1] + X[:, 2]
    y = (decision > 0).astype(int)
    
    return X, y


# Convenience function for quick testing
def get_test_datasets() -> dict:
    """
    Get a dictionary of all test datasets.
    
    Returns:
        dict: Mapping of dataset names to (X, y) tuples.
    """
    return {
        "diagonal": make_diagonal_dataset(n_samples=100, random_state=42),
        "xor": make_xor_dataset(n_samples=200, random_state=42),
        "oblique_45": make_oblique_classification(n_samples=100, angle=45, random_state=42),
        "oblique_30": make_oblique_classification(n_samples=100, angle=30, random_state=42),
        "multiclass_3": make_multiclass_oblique(n_samples=150, n_classes=3, random_state=42),
        "nested": make_nested_rectangles(n_samples=200, random_state=42),
        "3d_oblique": make_3d_oblique(n_samples=200, random_state=42),
    }
