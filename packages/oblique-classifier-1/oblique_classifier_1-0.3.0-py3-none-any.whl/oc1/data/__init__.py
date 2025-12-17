"""
OC1 Data Module

Provides synthetic test datasets and utilities for testing oblique decision trees.
"""

from oc1.data.datasets import (
    make_oblique_classification,
    make_xor_dataset,
    make_diagonal_dataset,
    make_multiclass_oblique,
    make_nested_rectangles,
)

__all__ = [
    "make_oblique_classification",
    "make_xor_dataset",
    "make_diagonal_dataset",
    "make_multiclass_oblique",
    "make_nested_rectangles",
]
