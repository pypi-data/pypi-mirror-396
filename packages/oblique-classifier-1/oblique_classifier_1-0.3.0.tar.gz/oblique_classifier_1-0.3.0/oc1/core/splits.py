"""
OC1 Split Evaluation and Impurity Measures

This module implements the split evaluation functions as specified in the OC1 paper
"OC1: A randomized algorithm for building oblique decision trees" by Murthy et al. (1992).

Paper Reference:
- Section 2: Hyperplane partitioning (V_j > 0 → Left, V_j ≤ 0 → Right)
- Section 2.4: Impurity measures (Sum Minority and Max Minority)

Key Functions:
- partition_data: Partition samples based on hyperplane evaluation
- calculate_impurity: Compute SM and MM impurity measures
- compute_class_counts: Count samples per class in a subset
- evaluate_hyperplane: Compute V_j values for all samples
"""

from typing import Any, Dict, Tuple
import numpy as np


def evaluate_hyperplane(X: np.ndarray, hyperplane: np.ndarray) -> np.ndarray:
    """
    Evaluate the hyperplane for all samples.
    
    Computes V_j = ∑_{i=1}^{d} (a_i * x_j^i) + a_{d+1} for each sample j.
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        hyperplane: Coefficients [a₁, ..., a_d, a_{d+1}] of shape (n_features + 1,).
    
    Returns:
        np.ndarray: V_j values of shape (n_samples,).
            - V_j > 0: sample goes to left child
            - V_j ≤ 0: sample goes to right child
    
    Paper Reference: Section 2 - Hyperplane evaluation
    
    Example:
        >>> X = np.array([[1, 2], [3, 4]])
        >>> hyperplane = np.array([1.0, -1.0, 0.0])  # x1 - x2 = 0
        >>> V = evaluate_hyperplane(X, hyperplane)
        >>> V  # [1*1 + (-1)*2 + 0, 1*3 + (-1)*4 + 0] = [-1, -1]
    """
    X = np.atleast_2d(X)
    n_samples, n_features = X.shape
    
    if len(hyperplane) != n_features + 1:
        raise ValueError(
            f"Hyperplane has {len(hyperplane)} coefficients but "
            f"data has {n_features} features (expected {n_features + 1})"
        )
    
    # V_j = ∑(a_i * x_j^i) + a_{d+1} = X @ a[:-1] + a[-1]
    V = X @ hyperplane[:-1] + hyperplane[-1]
    
    return V


def partition_data(
    X: np.ndarray,
    y: np.ndarray,
    hyperplane: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Partition data into left and right subsets based on hyperplane.
    
    Following the OC1 paper partitioning rule (Section 2):
    - Left partition: V_j > 0
    - Right partition: V_j ≤ 0
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Class labels of shape (n_samples,).
        hyperplane: Coefficients [a₁, ..., a_d, a_{d+1}].
    
    Returns:
        Tuple containing:
            - X_left: Features for left partition
            - y_left: Labels for left partition
            - X_right: Features for right partition
            - y_right: Labels for right partition
            - V: Hyperplane evaluations for all samples
    
    Paper Reference: Section 2 - Partitioning rule
    
    Example:
        >>> X = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        >>> y = np.array([0, 1, 0, 1])
        >>> hp = np.array([1.0, 1.0, -1.5])  # x + y - 1.5 = 0
        >>> X_l, y_l, X_r, y_r, V = partition_data(X, y, hp)
        >>> # Points (1,1) go left (V > 0), others go right
    """
    X = np.atleast_2d(X)
    y = np.atleast_1d(y)
    
    if len(X) != len(y):
        raise ValueError(f"X has {len(X)} samples but y has {len(y)}")
    
    V = evaluate_hyperplane(X, hyperplane)
    
    # Left: V > 0, Right: V <= 0 (Section 2)
    left_mask = V > 0
    right_mask = ~left_mask
    
    X_left = X[left_mask]
    y_left = y[left_mask]
    X_right = X[right_mask]
    y_right = y[right_mask]
    
    return X_left, y_left, X_right, y_right, V


def compute_class_counts(y: np.ndarray) -> Dict[Any, int]:
    """
    Compute the count of each class in the label array.
    
    Args:
        y: Class labels of shape (n_samples,).
    
    Returns:
        Dict mapping class labels to their counts.
    
    Example:
        >>> y = np.array([0, 1, 0, 2, 1, 0])
        >>> compute_class_counts(y)
        {0: 3, 1: 2, 2: 1}
    """
    y = np.atleast_1d(y)
    unique, counts = np.unique(y, return_counts=True)
    return dict(zip(unique, counts))


def compute_minority(class_counts: Dict[Any, int]) -> int:
    """
    Compute the minority count (minimum class count).
    
    For impurity calculations, the minority is defined as the minimum count
    among all classes present in the partition.
    
    Args:
        class_counts: Dict mapping class labels to counts.
    
    Returns:
        int: Minimum class count (0 if empty or single class).
    
    Paper Reference: Section 2.4 - Minority definition for impurity
    
    Example:
        >>> compute_minority({0: 10, 1: 3, 2: 5})
        3
        >>> compute_minority({0: 10})  # Pure node
        0
    """
    if not class_counts:
        return 0
    counts = list(class_counts.values())
    if len(counts) <= 1:
        return 0
    return min(counts)


def calculate_impurity(
    class_counts_left: Dict[Any, int],
    class_counts_right: Dict[Any, int],
) -> Tuple[float, float]:
    """
    Calculate Sum Minority (SM) and Max Minority (MM) impurity measures.
    
    From Section 2.4 of the OC1 paper:
    - minority_L = min(count of each class in L)
    - minority_R = min(count of each class in R)
    - Sum Minority (SM) = minority_L + minority_R
    - Max Minority (MM) = max(minority_L, minority_R)
    
    LOWER impurity = BETTER split (we want to minimize misclassified samples).
    
    Args:
        class_counts_left: Dict mapping class labels to counts in left partition.
        class_counts_right: Dict mapping class labels to counts in right partition.
    
    Returns:
        Tuple[float, float]: (SM impurity, MM impurity)
    
    Paper Reference: Section 2.4 - Impurity measure definitions
    
    Example:
        >>> # Left has 8 class-0 and 2 class-1, Right has 3 class-0 and 7 class-1
        >>> left = {0: 8, 1: 2}
        >>> right = {0: 3, 1: 7}
        >>> sm, mm = calculate_impurity(left, right)
        >>> sm  # 2 + 3 = 5
        5.0
        >>> mm  # max(2, 3) = 3
        3.0
    """
    minority_left = compute_minority(class_counts_left)
    minority_right = compute_minority(class_counts_right)
    
    sm = float(minority_left + minority_right)
    mm = float(max(minority_left, minority_right))
    
    return sm, mm


def calculate_impurity_from_partition(
    y_left: np.ndarray,
    y_right: np.ndarray,
) -> Tuple[float, float]:
    """
    Calculate impurity directly from label arrays.
    
    Convenience function that computes class counts and impurity in one call.
    
    Args:
        y_left: Class labels in left partition.
        y_right: Class labels in right partition.
    
    Returns:
        Tuple[float, float]: (SM impurity, MM impurity)
    
    Paper Reference: Section 2.4
    """
    counts_left = compute_class_counts(y_left)
    counts_right = compute_class_counts(y_right)
    return calculate_impurity(counts_left, counts_right)


def evaluate_split(
    X: np.ndarray,
    y: np.ndarray,
    hyperplane: np.ndarray,
    impurity_measure: str = "sm",
) -> float:
    """
    Evaluate a hyperplane split using the specified impurity measure.
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Class labels of shape (n_samples,).
        hyperplane: Coefficients [a₁, ..., a_d, a_{d+1}].
        impurity_measure: "sm" for Sum Minority or "mm" for Max Minority.
    
    Returns:
        float: The impurity value (lower is better).
    
    Paper Reference: Section 2.4
    """
    impurity_measure = impurity_measure.lower()
    if impurity_measure not in ("sm", "mm"):
        raise ValueError(f"impurity_measure must be 'sm' or 'mm', got {impurity_measure}")
    
    _, y_left, _, y_right, _ = partition_data(X, y, hyperplane)
    sm, mm = calculate_impurity_from_partition(y_left, y_right)
    
    return sm if impurity_measure == "sm" else mm


def find_best_threshold(
    values: np.ndarray,
    y: np.ndarray,
    impurity_measure: str = "sm",
) -> Tuple[float, float]:
    """
    Find the best threshold for a univariate split on given values.
    
    This is used in coefficient perturbation to find the optimal value
    for coefficient a_m by treating the U_j values as a 1D split problem.
    
    Args:
        values: 1D array of values to split on.
        y: Class labels corresponding to each value.
        impurity_measure: "sm" for Sum Minority or "mm" for Max Minority.
    
    Returns:
        Tuple[float, float]: (best_threshold, best_impurity)
    
    Paper Reference: Section 2.2 - Finding best univariate split on U_j values
    """
    values = np.atleast_1d(values).ravel()
    y = np.atleast_1d(y).ravel()
    
    if len(values) != len(y):
        raise ValueError(f"values has {len(values)} samples but y has {len(y)}")
    
    if len(values) == 0:
        return 0.0, float('inf')
    
    if len(values) == 1:
        return values[0], 0.0
    
    # Sort values and corresponding labels
    sorted_indices = np.argsort(values)
    sorted_values = values[sorted_indices]
    sorted_y = y[sorted_indices]
    
    # Find unique thresholds (midpoints between consecutive distinct values)
    unique_values = np.unique(sorted_values)
    
    if len(unique_values) == 1:
        # All values are identical - no meaningful split
        return unique_values[0], float('inf')
    
    # Generate candidate thresholds as midpoints
    thresholds = (unique_values[:-1] + unique_values[1:]) / 2
    
    best_threshold = thresholds[0]
    best_impurity = float('inf')
    
    for threshold in thresholds:
        # Split: left if value > threshold, right if value <= threshold
        left_mask = sorted_values > threshold
        y_left = sorted_y[left_mask]
        y_right = sorted_y[~left_mask]
        
        sm, mm = calculate_impurity_from_partition(y_left, y_right)
        impurity = sm if impurity_measure.lower() == "sm" else mm
        
        if impurity < best_impurity:
            best_impurity = impurity
            best_threshold = threshold
    
    return best_threshold, best_impurity


def is_pure(y: np.ndarray) -> bool:
    """
    Check if all samples belong to the same class.
    
    A pure node has zero impurity and should not be split further.
    
    Args:
        y: Class labels.
    
    Returns:
        bool: True if all samples have the same class.
    
    Paper Reference: Section 2.4 - Stop splitting at zero impurity
    """
    y = np.atleast_1d(y)
    if len(y) == 0:
        return True
    return len(np.unique(y)) <= 1


def get_majority_class(y: np.ndarray) -> Any:
    """
    Get the majority class from a label array.
    
    Args:
        y: Class labels.
    
    Returns:
        The class label with the highest count.
    """
    y = np.atleast_1d(y)
    if len(y) == 0:
        return None
    unique, counts = np.unique(y, return_counts=True)
    return unique[np.argmax(counts)]
