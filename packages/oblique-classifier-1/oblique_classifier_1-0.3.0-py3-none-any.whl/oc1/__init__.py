"""
OC1: Oblique Classifier 1 - Implementation of Murthy et al. (1992)

A Python implementation of the OC1 oblique decision tree algorithm as described in:
"OC1: A randomized algorithm for building oblique decision trees"
by Sreerama K. Murthy, Simon Kasif, Steven Salzberg, and Richard Beigel.
AAAI-1992.

This package provides:
- ObliqueTreeNode: Node representation with hyperplane coefficients
- ObliqueDecisionTree: Main classifier implementing the OC1 algorithm
- Impurity measures: Sum Minority (SM) and Max Minority (MM)
- Coefficient perturbation and hill-climbing optimization
- Export methods: to_dict(), to_json(), to_dot()

Task 1 Implementation - Core Tree Construction (Deterministic)
Task 2 Implementation - Randomization (Multiple restarts, random perturbation)
Task 3 Implementation - Pruning, Logging, Evaluation, Visualization
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

# Task 3: Evaluation module
from oc1.evaluation import (
    cross_validate,
    train_test_split,
    confusion_matrix,
    classification_report,
)

# Task 3: Visualization module (optional, requires matplotlib)
try:
    from oc1.visualization import (
        plot_decision_boundary_2d,
        plot_hyperplanes_2d,
        plot_tree_structure,
    )
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# Task 3: Logging module
from oc1.core.logging import (
    TreeConstructionLogger,
    get_default_logger,
)

__version__ = "0.3.0"  # Updated with export features
__author__ = "OC1 Implementation Team"
__paper__ = "Murthy et al., OC1: A randomized algorithm for building oblique decision trees, AAAI-1992"

__all__ = [
    # Core classes
    "ObliqueTreeNode",
    "ObliqueDecisionTree",
    # Split evaluation
    "partition_data",
    "calculate_impurity",
    "compute_class_counts",
    "evaluate_hyperplane",
    "evaluate_split",
    "is_pure",
    "get_majority_class",
    # Hill climbing
    "perturb_coefficient",
    "hill_climb",
    "initialize_hyperplane",
    "find_best_hyperplane",
    "normalize_hyperplane",
    "compute_u_values",
    "perturb_random_direction",
    # Task 3: Evaluation
    "cross_validate",
    "train_test_split",
    "confusion_matrix",
    "classification_report",
    # Task 3: Logging
    "TreeConstructionLogger",
    "get_default_logger",
]

# Add visualization if available
if VISUALIZATION_AVAILABLE:
    __all__.extend([
        "plot_decision_boundary_2d",
        "plot_hyperplanes_2d",
        "plot_tree_structure",
    ])
