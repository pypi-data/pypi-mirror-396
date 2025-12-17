"""
OC1 Coefficient Perturbation and Hill-Climbing Optimization

This module implements the deterministic hill-climbing algorithm as specified in the OC1 paper
"OC1: A randomized algorithm for building oblique decision trees" by Murthy et al. (1992).

Paper Reference:
- Section 2.1: Deterministic hill-climbing (sequential coefficient perturbation)
- Section 2.2: Coefficient perturbation algorithm (Equation 1)
- Section 2.3: Randomization extensions (prepared for Task 2)

Key Functions:
- perturb_coefficient: Optimize one coefficient using Equation 1
- hill_climb: Full deterministic hill-climbing optimization
- initialize_hyperplane: Create initial hyperplane for optimization
"""

from typing import List, Optional, Tuple
import numpy as np

from oc1.core.splits import (
    partition_data,
    calculate_impurity_from_partition,
    evaluate_hyperplane,
    evaluate_split,
    find_best_threshold,
)


def initialize_hyperplane(
    X: np.ndarray,
    y: np.ndarray,
    method: str = "axis_parallel",
    random_state: Optional[int] = None,
) -> np.ndarray:
    """
    Initialize a hyperplane for hill-climbing optimization.
    
    Provides different initialization strategies:
    - "axis_parallel": Start with the best axis-parallel split (feature-aligned)
    - "random": Random coefficients (useful for Task 2 randomization)
    - "zeros": All zeros except bias term (for testing)
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Class labels of shape (n_samples,).
        method: Initialization method ("axis_parallel", "random", "zeros").
        random_state: Random seed for reproducibility (used in "random" method).
    
    Returns:
        np.ndarray: Initial hyperplane coefficients [a₁, ..., a_d, a_{d+1}].
    
    Paper Reference: Section 2.1 - Starting point for hill-climbing
    """
    X = np.atleast_2d(X)
    n_samples, n_features = X.shape
    
    if random_state is not None:
        np.random.seed(random_state)
    
    method = method.lower()
    
    if method == "zeros":
        # Initialize with zeros (useful for testing)
        hyperplane = np.zeros(n_features + 1)
        hyperplane[-1] = 1.0  # Non-zero bias to avoid degenerate case
        return hyperplane
    
    elif method == "random":
        # Random initialization (for Task 2 randomization)
        hyperplane = np.random.randn(n_features + 1)
        # Normalize to unit length for numerical stability
        norm = np.linalg.norm(hyperplane[:-1])
        if norm > 1e-10:
            hyperplane[:-1] /= norm
        return hyperplane
    
    elif method == "axis_parallel":
        # Find best axis-parallel (single feature) split
        # This is equivalent to a standard decision stump
        best_hyperplane = np.zeros(n_features + 1)
        best_impurity = float('inf')
        
        for feature_idx in range(n_features):
            feature_values = X[:, feature_idx]
            threshold, impurity = find_best_threshold(feature_values, y, "sm")
            
            if impurity < best_impurity:
                best_impurity = impurity
                best_hyperplane = np.zeros(n_features + 1)
                best_hyperplane[feature_idx] = 1.0
                best_hyperplane[-1] = -threshold  # a_i * x_i + a_{d+1} = 0 → x_i = -a_{d+1}
        
        # If no good split found, use first feature with midpoint
        if np.allclose(best_hyperplane, 0):
            best_hyperplane[0] = 1.0
            best_hyperplane[-1] = -np.median(X[:, 0])
        
        return best_hyperplane
    
    else:
        raise ValueError(f"Unknown initialization method: {method}")


def compute_u_values(
    X: np.ndarray,
    hyperplane: np.ndarray,
    m: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute U_j values for coefficient perturbation (Equation 1 from paper).
    
    For coefficient a_m, we compute for each example j:
        U_j = a_m * x_j^m - V_j / x_j^m
    
    where V_j = ∑(a_i * x_j^i) + a_{d+1}
    
    This transforms the oblique split optimization into a univariate problem.
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        hyperplane: Current hyperplane coefficients [a₁, ..., a_d, a_{d+1}].
        m: Index of the coefficient to perturb (0 to d for features, d for bias).
    
    Returns:
        Tuple containing:
            - U_j values of shape (n_valid,) for samples where computation is valid
            - valid_mask: Boolean mask indicating which samples have valid U_j
    
    Paper Reference: Section 2.2, Equation 1
    
    Note:
        When x_j^m = 0 (or very small), U_j is undefined. These samples are excluded.
        For the bias term (m = d), x_j^m is treated as 1.
    """
    X = np.atleast_2d(X)
    n_samples, n_features = X.shape
    
    # Validate coefficient index
    if m < 0 or m > n_features:
        raise ValueError(f"Coefficient index m={m} out of range [0, {n_features}]")
    
    # Compute V_j for all samples
    V = evaluate_hyperplane(X, hyperplane)
    
    # Get the feature values for coefficient m
    if m < n_features:
        # Feature coefficient
        x_m = X[:, m]
    else:
        # Bias term (a_{d+1}): treat as if x_j^m = 1
        x_m = np.ones(n_samples)
    
    # Handle division by zero: exclude samples where x_m is too small
    epsilon = 1e-10
    valid_mask = np.abs(x_m) > epsilon
    
    if not np.any(valid_mask):
        # No valid samples - return empty arrays
        return np.array([]), valid_mask
    
    # Compute U_j = a_m * x_j^m - V_j / x_j^m for valid samples
    a_m = hyperplane[m]
    U = np.full(n_samples, np.nan)
    U[valid_mask] = a_m * x_m[valid_mask] - V[valid_mask] / x_m[valid_mask]
    
    return U, valid_mask


def perturb_coefficient(
    X: np.ndarray,
    y: np.ndarray,
    hyperplane: np.ndarray,
    m: int,
    impurity_measure: str = "sm",
) -> Tuple[np.ndarray, float, bool]:
    """
    Perturb a single coefficient to find the optimal value (Section 2.2).
    
    This implements the coefficient perturbation algorithm from the OC1 paper:
    1. Compute U_j = a_m * x_j^m - V_j / x_j^m for each valid example j
    2. Find the best univariate threshold on the U_j values
    3. Set a_m to the optimal threshold
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Class labels of shape (n_samples,).
        hyperplane: Current hyperplane coefficients [a₁, ..., a_d, a_{d+1}].
        m: Index of the coefficient to perturb (0 to d).
        impurity_measure: "sm" for Sum Minority or "mm" for Max Minority.
    
    Returns:
        Tuple containing:
            - new_hyperplane: Updated hyperplane with optimized a_m
            - new_impurity: Impurity after perturbation
            - improved: True if impurity was reduced
    
    Paper Reference: Section 2.2, Equation 1
    
    Example:
        >>> X = np.array([[1, 2], [2, 1], [3, 4], [4, 3]])
        >>> y = np.array([0, 0, 1, 1])
        >>> hp = np.array([1.0, 0.0, -2.5])
        >>> new_hp, imp, improved = perturb_coefficient(X, y, hp, 0)
    """
    X = np.atleast_2d(X)
    y = np.atleast_1d(y)
    n_samples, n_features = X.shape
    
    # Get current impurity
    _, y_left, _, y_right, _ = partition_data(X, y, hyperplane)
    current_sm, current_mm = calculate_impurity_from_partition(y_left, y_right)
    current_impurity = current_sm if impurity_measure.lower() == "sm" else current_mm
    
    # Compute U_j values
    U, valid_mask = compute_u_values(X, hyperplane, m)
    
    # Filter to valid samples
    valid_U = U[valid_mask]
    valid_y = y[valid_mask]
    
    if len(valid_U) < 2:
        # Not enough valid samples to find a split
        return hyperplane.copy(), current_impurity, False
    
    # Find best threshold on U_j values
    best_threshold, _ = find_best_threshold(valid_U, valid_y, impurity_measure)
    
    # Create new hyperplane with updated coefficient
    new_hyperplane = hyperplane.copy()
    new_hyperplane[m] = best_threshold
    
    # Evaluate new hyperplane
    _, y_left_new, _, y_right_new, _ = partition_data(X, y, new_hyperplane)
    new_sm, new_mm = calculate_impurity_from_partition(y_left_new, y_right_new)
    new_impurity = new_sm if impurity_measure.lower() == "sm" else new_mm
    
    improved = new_impurity < current_impurity
    
    if improved:
        return new_hyperplane, new_impurity, True
    else:
        return hyperplane.copy(), current_impurity, False


def hill_climb(
    X: np.ndarray,
    y: np.ndarray,
    initial_hyperplane: Optional[np.ndarray] = None,
    impurity_measure: str = "sm",
    max_iterations: int = 100,
    tolerance: float = 1e-10,
    perturbation_order: Optional[List[int]] = None,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[np.ndarray, float, int]:
    """
    Perform deterministic hill-climbing optimization (Section 2.1).
    
    This implements the sequential perturbation strategy from the OC1 paper:
    1. Start with initial hyperplane H
    2. For each coefficient m = 1 to d+1:
       a. Perturb a_m using Equation 1 method
       b. If new impurity < current impurity: accept new a_m
    3. Repeat until no improvements across all coefficients (local minimum)
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Class labels of shape (n_samples,).
        initial_hyperplane: Starting hyperplane (auto-initialized if None).
        impurity_measure: "sm" for Sum Minority or "mm" for Max Minority.
        max_iterations: Maximum number of full passes through all coefficients.
        tolerance: Minimum improvement required to continue.
        perturbation_order: Optional list of coefficient indices specifying
            the order in which to perturb coefficients. If None, uses
            sequential order [0, 1, ..., d]. Task 2 will use random orders.
        rng: NumPy random generator for reproducibility (Task 2 hook).
    
    Returns:
        Tuple containing:
            - best_hyperplane: Optimized hyperplane coefficients
            - best_impurity: Final impurity value
            - n_iterations: Number of iterations performed
    
    Paper Reference: Section 2.1 - Deterministic sequential perturbation
    
    Example:
        >>> X = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        >>> y = np.array([0, 1, 1, 0])  # XOR problem
        >>> hp, imp, iters = hill_climb(X, y)
    """
    X = np.atleast_2d(X)
    y = np.atleast_1d(y)
    n_samples, n_features = X.shape
    
    if n_samples == 0:
        raise ValueError("Cannot perform hill-climbing on empty dataset")
    
    # Initialize hyperplane if not provided
    if initial_hyperplane is None:
        hyperplane = initialize_hyperplane(X, y, method="axis_parallel")
    else:
        hyperplane = initial_hyperplane.copy()
    
    # Validate hyperplane dimensions
    if len(hyperplane) != n_features + 1:
        raise ValueError(
            f"Hyperplane has {len(hyperplane)} coefficients but "
            f"expected {n_features + 1}"
        )
    
    # Compute initial impurity
    _, y_left, _, y_right, _ = partition_data(X, y, hyperplane)
    sm, mm = calculate_impurity_from_partition(y_left, y_right)
    current_impurity = sm if impurity_measure.lower() == "sm" else mm
    
    best_hyperplane = hyperplane.copy()
    best_impurity = current_impurity
    
    # Use provided perturbation order or default sequential
    if perturbation_order is None:
        perturbation_order = list(range(n_features + 1))
    
    # Hill-climbing loop
    n_iterations = 0
    for iteration in range(max_iterations):
        improved_this_pass = False
        
        # Cycle through all coefficients in specified order
        for m in perturbation_order:
            new_hp, new_imp, improved = perturb_coefficient(
                X, y, hyperplane, m, impurity_measure
            )
            
            if improved and (best_impurity - new_imp) > tolerance:
                hyperplane = new_hp
                current_impurity = new_imp
                improved_this_pass = True
                
                if new_imp < best_impurity:
                    best_hyperplane = new_hp.copy()
                    best_impurity = new_imp
        
        n_iterations = iteration + 1
        
        # Stop if no improvements in this pass (local minimum reached)
        if not improved_this_pass:
            break
        
        # Stop if impurity is zero (perfect split)
        if best_impurity <= tolerance:
            break
    
    return best_hyperplane, best_impurity, n_iterations


def find_best_hyperplane(
    X: np.ndarray,
    y: np.ndarray,
    impurity_measure: str = "sm",
    n_restarts: int = 1,
    max_iterations: int = 100,
    random_state: Optional[int] = None,
    use_random_perturbation_order: bool = False,
) -> Tuple[np.ndarray, float]:
    """
    Find the best hyperplane using hill-climbing with optional restarts.
    
    This is the main entry point for hyperplane optimization, designed to be
    compatible with Task 2 randomization extensions.
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Class labels of shape (n_samples,).
        impurity_measure: "sm" for Sum Minority or "mm" for Max Minority.
        n_restarts: Number of random restarts (1 for deterministic, >1 for Task 2).
        max_iterations: Maximum hill-climbing iterations per restart.
        random_state: Random seed for reproducibility. Uses np.random.default_rng()
            for proper seed propagation across all random operations.
        use_random_perturbation_order: If True, randomize the order of coefficient
            perturbation in each hill-climbing pass (Task 2 enhancement).
    
    Returns:
        Tuple containing:
            - best_hyperplane: Best hyperplane found across all restarts
            - best_impurity: Corresponding impurity value
    
    Paper Reference: Section 2.1 (deterministic), Section 2.3 (randomization for Task 2)
    """
    X = np.atleast_2d(X)
    y = np.atleast_1d(y)
    n_features = X.shape[1]
    
    # Use modern RNG for proper seed propagation
    rng = np.random.default_rng(random_state)
    
    best_hyperplane = None
    best_impurity = float('inf')
    
    for restart in range(n_restarts):
        # For first restart (or deterministic mode), use axis-parallel initialization
        # For subsequent restarts, use random initialization (Task 2 extension point)
        if restart == 0:
            initial_hp = initialize_hyperplane(X, y, method="axis_parallel")
        else:
            # Random initialization using RNG for proper seed propagation
            initial_hp = rng.standard_normal(n_features + 1)
            initial_hp = normalize_hyperplane(initial_hp)
        
        # Determine perturbation order
        if use_random_perturbation_order:
            perturbation_order = list(range(n_features + 1))
            rng.shuffle(perturbation_order)
        else:
            perturbation_order = None  # Use default sequential order
        
        hp, impurity, _ = hill_climb(
            X, y,
            initial_hyperplane=initial_hp,
            impurity_measure=impurity_measure,
            max_iterations=max_iterations,
            perturbation_order=perturbation_order,
            rng=rng,
        )
        
        # TASK 2: Multi-coefficient perturbation enhancement
        if n_restarts > 1:  # Only apply for randomized mode
            hp_multi, imp_multi = perturb_multiple_coefficients(
                X, y, hp, impurity_measure, n_coefficients=3, n_trials=10, rng=rng
            )
            if imp_multi < impurity:
                hp, impurity = hp_multi, imp_multi
        
        # Keep best across all restarts
        if impurity < best_impurity:
            best_hyperplane = hp
            best_impurity = impurity
    
    return best_hyperplane, best_impurity


def normalize_hyperplane(hyperplane: np.ndarray) -> np.ndarray:
    """
    Normalize hyperplane coefficients for numerical stability.
    
    Scales the coefficients so that the feature coefficients have unit norm.
    This doesn't change the hyperplane's decision boundary.
    
    Args:
        hyperplane: Coefficients [a₁, ..., a_d, a_{d+1}].
    
    Returns:
        Normalized hyperplane coefficients.
    """
    hyperplane = np.atleast_1d(hyperplane).astype(float)
    
    # Normalize by the norm of feature coefficients (excluding bias)
    feature_norm = np.linalg.norm(hyperplane[:-1])
    
    if feature_norm > 1e-10:
        return hyperplane / feature_norm
    else:
        return hyperplane.copy()


def perturb_random_direction(
    X: np.ndarray,
    y: np.ndarray,
    hyperplane: np.ndarray,
    impurity_measure: str = "sm",
    n_directions: int = 10,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[np.ndarray, float]:
    """
    Perturb hyperplane in random directions (multi-coefficient perturbation).
    
    This is a hook for Task 2 randomization. It perturbs multiple coefficients
    simultaneously by adding random direction vectors to the hyperplane.
    Unlike the sequential single-coefficient perturbation in hill_climb(),
    this explores the solution space more broadly.
    
    Paper Reference: Section 3 - Randomization enhancements
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Class labels of shape (n_samples,).
        hyperplane: Current hyperplane coefficients [a_1, ..., a_d, a_{d+1}].
        impurity_measure: "sm" for Sum Minority or "mm" for Max Minority.
        n_directions: Number of random directions to try.
        rng: NumPy random generator for reproducibility.
    
    Returns:
        Tuple[np.ndarray, float]: (best_hyperplane, best_impurity)
    
    Example:
        >>> X = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        >>> y = np.array([0, 1, 1, 0])
        >>> hp = np.array([1.0, 0.0, -0.5])
        >>> rng = np.random.default_rng(42)
        >>> new_hp, imp = perturb_random_direction(X, y, hp, rng=rng)
    """
    if rng is None:
        rng = np.random.default_rng()
    
    best_hyperplane = hyperplane.copy()
    best_impurity = evaluate_split(X, y, hyperplane, impurity_measure)
    
    n_features = len(hyperplane) - 1
    
    for _ in range(n_directions):
        # Generate random direction vector
        direction = rng.standard_normal(n_features + 1)
        
        # Try different step sizes
        for step_size in [0.1, 0.5, 1.0]:
            perturbed = hyperplane + step_size * direction
            
            # Normalize to prevent coefficient explosion
            perturbed = normalize_hyperplane(perturbed)
            
            impurity = evaluate_split(X, y, perturbed, impurity_measure)
            
            if impurity < best_impurity:
                best_impurity = impurity
                best_hyperplane = perturbed.copy()
    
    return best_hyperplane, best_impurity


def perturb_multiple_coefficients(
    X: np.ndarray,
    y: np.ndarray,
    hyperplane: np.ndarray,
    impurity_measure: str = "sm",
    n_coefficients: int = 3,
    n_trials: int = 10,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[np.ndarray, float]:
    """
    Task 2: Perturb multiple coefficients simultaneously to escape local minima.
    
    Changes multiple hyperplane coefficients at once by moving in random
    directions through coefficient space.
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Class labels of shape (n_samples,).
        hyperplane: Current hyperplane coefficients [a_1, ..., a_d, a_{d+1}].
        impurity_measure: "sm" for Sum Minority or "mm" for Max Minority.
        n_coefficients: Number of coefficients to perturb simultaneously.
        n_trials: Number of random trials to attempt.
        rng: NumPy random generator for reproducibility.
    
    Returns:
        Tuple[np.ndarray, float]: (best_hyperplane, best_impurity)
    
    Paper Reference: Section 2.3 - Randomization enhancements
    """
    if rng is None:
        rng = np.random.default_rng()
    
    n_features = len(hyperplane) - 1
    best_hyperplane = hyperplane.copy()
    best_impurity = evaluate_split(X, y, hyperplane, impurity_measure)
    
    # Limit n_coefficients to available coefficients
    n_coeffs = min(n_coefficients, n_features + 1)
    
    for _ in range(n_trials):
        # Select random subset of coefficients
        indices = rng.choice(n_features + 1, size=n_coeffs, replace=False)
        
        # Generate random direction
        direction = np.zeros(n_features + 1)
        direction[indices] = rng.standard_normal(n_coeffs)
        
        # Normalize direction
        norm = np.linalg.norm(direction)
        if norm > 1e-10:
            direction = direction / norm
        else:
            continue
        
        # Try different step sizes
        for step in [0.1, 0.5, 1.0]:
            trial_hp = hyperplane + step * direction
            trial_hp = normalize_hyperplane(trial_hp)
            
            trial_imp = evaluate_split(X, y, trial_hp, impurity_measure)
            
            if trial_imp < best_impurity:
                best_impurity = trial_imp
                best_hyperplane = trial_hp.copy()
    
    return best_hyperplane, best_impurity


def validate_hyperplane(
    hyperplane: np.ndarray,
    rng: Optional[np.random.Generator] = None
) -> Tuple[np.ndarray, bool]:
    """
    Task 2: Validate and fix degenerate hyperplanes.
    
    Checks for NaN, infinity, zero weights, and extreme values,
    and attempts to fix them by generating a new random hyperplane.
    
    Args:
        hyperplane: Hyperplane coefficients to validate.
        rng: NumPy random generator for reproducibility.
    
    Returns:
        Tuple[np.ndarray, bool]: (fixed_hyperplane, is_valid)
            - fixed_hyperplane: The validated/fixed hyperplane
            - is_valid: True if original hyperplane was valid, False if fixed
    """
    if rng is None:
        rng = np.random.default_rng()
    
    fixed = hyperplane.copy()
    valid = True
    n_features = len(hyperplane) - 1
    
    # Fix NaN
    if np.any(np.isnan(fixed)):
        fixed = rng.standard_normal(n_features + 1)
        fixed = normalize_hyperplane(fixed)
        valid = False
    
    # Fix infinity
    if np.any(np.isinf(fixed)):
        fixed = np.clip(fixed, -10.0, 10.0)
        valid = False
    
    # Fix zero weights
    if np.allclose(fixed[:-1], 0):
        fixed = rng.standard_normal(n_features + 1)
        fixed = normalize_hyperplane(fixed)
        valid = False
    
    # Fix extreme values
    if np.max(np.abs(fixed)) > 1e6:
        fixed = normalize_hyperplane(fixed)
        valid = False
    
    return fixed, valid
