"""
OC1 Core Module

Contains core implementations of the OC1 algorithm components.
"""

from oc1.core.node import ObliqueTreeNode
from oc1.core.tree import ObliqueDecisionTree
from oc1.core.splits import (
    partition_data,
    calculate_impurity,
    compute_class_counts,
    evaluate_hyperplane,
    evaluate_split,
    is_pure,
    get_majority_class,
)
from oc1.core.hill_climb import (
    perturb_coefficient,
    hill_climb,
    initialize_hyperplane,
    find_best_hyperplane,
    normalize_hyperplane,
    compute_u_values,
    perturb_random_direction,
)

__all__ = [
    "ObliqueTreeNode",
    "ObliqueDecisionTree",
    "partition_data",
    "calculate_impurity",
    "compute_class_counts",
    "evaluate_hyperplane",
    "evaluate_split",
    "is_pure",
    "get_majority_class",
    "perturb_coefficient",
    "hill_climb",
    "initialize_hyperplane",
    "find_best_hyperplane",
    "normalize_hyperplane",
    "compute_u_values",
    "perturb_random_direction",
]
