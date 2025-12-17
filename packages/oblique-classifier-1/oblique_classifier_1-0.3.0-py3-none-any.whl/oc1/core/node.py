"""
OC1 Oblique Tree Node Implementation

This module implements the ObliqueTreeNode class as specified in the OC1 paper
"OC1: A randomized algorithm for building oblique decision trees" by Murthy et al. (1992).

Paper Reference:
- Section 2: Hyperplane definition and tree structure
- Each non-leaf node contains hyperplane coefficients [a₁, a₂, ..., a_d, a_{d+1}]
- Hyperplane equation: ∑(a_i * x_i) + a_{d+1} = 0
"""

from __future__ import annotations
from typing import Any, Dict, Optional
import numpy as np


class ObliqueTreeNode:
    """
    A node in an oblique decision tree.
    
    Each non-leaf node contains a hyperplane that partitions the feature space.
    The hyperplane is defined by coefficients [a₁, a₂, ..., a_d, a_{d+1}] where:
    - d is the number of features
    - The hyperplane equation is: ∑_{i=1}^{d} (a_i * x_i) + a_{d+1} = 0
    
    Partitioning rule (Section 2):
    - Left child: V_j > 0 (where V_j = ∑(a_i * x_j^i) + a_{d+1})
    - Right child: V_j ≤ 0
    
    Attributes:
        hyperplane: np.ndarray of shape (d+1,) containing coefficients [a₁, ..., a_d, a_{d+1}]
        class_distribution: Dict mapping class labels to counts at this node
        left_child: Left subtree (for samples where V_j > 0)
        right_child: Right subtree (for samples where V_j ≤ 0)
        parent: Parent node (None for root). Added for Task 3 pruning support.
        is_leaf: Whether this is a leaf node
        predicted_class: Class label predicted at this node (for leaves)
        depth: Depth of this node in the tree (root = 0)
        n_samples: Number of training samples at this node
        impurity: Impurity value at this node
    
    Paper Reference: Murthy et al., AAAI-1992, Section 2
    """
    
    def __init__(
        self,
        hyperplane: Optional[np.ndarray] = None,
        class_distribution: Optional[Dict[Any, int]] = None,
        is_leaf: bool = False,
        predicted_class: Optional[Any] = None,
        depth: int = 0,
        n_samples: int = 0,
        impurity: float = 0.0,
        parent: Optional['ObliqueTreeNode'] = None,
    ) -> None:
        """
        Initialize an ObliqueTreeNode.
        
        Args:
            hyperplane: Coefficients [a₁, ..., a_d, a_{d+1}] for the splitting hyperplane.
                       None for leaf nodes.
            class_distribution: Dict mapping class labels to sample counts.
            is_leaf: Whether this is a leaf node.
            predicted_class: The class to predict (for leaf nodes).
            depth: Depth of this node in the tree.
            n_samples: Number of training samples reaching this node.
            impurity: Impurity measure at this node.
            parent: Parent node reference (None for root). Used for Task 3 pruning.
        """
        self.hyperplane = hyperplane
        self.class_distribution = class_distribution if class_distribution is not None else {}
        self.left_child: Optional[ObliqueTreeNode] = None
        self.right_child: Optional[ObliqueTreeNode] = None
        self.parent: Optional[ObliqueTreeNode] = parent
        self.is_leaf = is_leaf
        self.predicted_class = predicted_class
        self.depth = depth
        self.n_samples = n_samples
        self.impurity = impurity
    
    def evaluate(self, X: np.ndarray) -> np.ndarray:
        """
        Evaluate the hyperplane for given samples.
        
        Computes V_j = ∑_{i=1}^{d} (a_i * x_j^i) + a_{d+1} for each sample.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features) or (n_features,)
        
        Returns:
            np.ndarray: V_j values for each sample. Positive values go left,
                       non-positive values go right.
        
        Paper Reference: Section 2 - Hyperplane evaluation formula
        """
        if self.hyperplane is None:
            raise ValueError("Cannot evaluate: node has no hyperplane (is leaf)")
        
        X = np.atleast_2d(X)
        n_features = X.shape[1]
        
        if len(self.hyperplane) != n_features + 1:
            raise ValueError(
                f"Hyperplane has {len(self.hyperplane)} coefficients but "
                f"data has {n_features} features (expected {n_features + 1})"
            )
        
        # V_j = ∑(a_i * x_j^i) + a_{d+1}
        # = X @ hyperplane[:-1] + hyperplane[-1]
        V = X @ self.hyperplane[:-1] + self.hyperplane[-1]
        
        return V
    
    def predict_single(self, x: np.ndarray) -> Any:
        """
        Predict the class for a single sample by traversing the tree.
        
        Args:
            x: Feature vector of shape (n_features,)
        
        Returns:
            Predicted class label.
        
        Paper Reference: Section 2 - Tree traversal based on V_j sign
        """
        if self.is_leaf:
            return self.predicted_class
        
        x = np.atleast_1d(x)
        V = self.evaluate(x.reshape(1, -1))[0]
        
        # Left if V > 0, Right if V <= 0 (Section 2)
        if V > 0:
            if self.left_child is None:
                return self.predicted_class
            return self.left_child.predict_single(x)
        else:
            if self.right_child is None:
                return self.predicted_class
            return self.right_child.predict_single(x)
    
    def get_majority_class(self) -> Any:
        """
        Get the majority class from the class distribution.
        
        Returns:
            The class label with the highest count.
        """
        if not self.class_distribution:
            return None
        return max(self.class_distribution, key=self.class_distribution.get)
    
    def get_minority_count(self) -> int:
        """
        Get the minority count for this node.
        
        The minority is the minimum count among all classes present.
        This is used in the impurity calculations (Section 2.4).
        
        Returns:
            int: Minimum class count (0 if node is empty or pure)
        
        Paper Reference: Section 2.4 - Impurity measure definitions
        """
        if not self.class_distribution:
            return 0
        counts = list(self.class_distribution.values())
        if len(counts) <= 1:
            return 0
        return min(counts)
    
    def is_pure(self) -> bool:
        """
        Check if this node contains only samples from one class.
        
        A pure node has zero impurity and should not be split further.
        
        Returns:
            bool: True if all samples belong to the same class.
        
        Paper Reference: Section 2.4 - Stop splitting at zero impurity
        """
        return len(self.class_distribution) <= 1
    
    def copy(self) -> 'ObliqueTreeNode':
        """
        Create a shallow copy of this node (without children or parent).
        
        Returns:
            A new ObliqueTreeNode with the same attributes.
        """
        node = ObliqueTreeNode(
            hyperplane=self.hyperplane.copy() if self.hyperplane is not None else None,
            class_distribution=self.class_distribution.copy(),
            is_leaf=self.is_leaf,
            predicted_class=self.predicted_class,
            depth=self.depth,
            n_samples=self.n_samples,
            impurity=self.impurity,
            parent=None,  # Don't copy parent reference
        )
        return node
    
    def __repr__(self) -> str:
        """String representation of the node."""
        if self.is_leaf:
            return (
                f"ObliqueTreeNode(leaf, class={self.predicted_class}, "
                f"n_samples={self.n_samples}, depth={self.depth})"
            )
        else:
            hp_str = (
                f"[{', '.join(f'{c:.3f}' for c in self.hyperplane)}]"
                if self.hyperplane is not None else "None"
            )
            return (
                f"ObliqueTreeNode(split, hyperplane={hp_str}, "
                f"n_samples={self.n_samples}, depth={self.depth})"
            )
    
    def get_tree_depth(self) -> int:
        """
        Get the maximum depth of the subtree rooted at this node.
        
        Returns:
            int: Maximum depth (0 for leaf nodes).
        """
        if self.is_leaf:
            return 0
        
        left_depth = self.left_child.get_tree_depth() if self.left_child else 0
        right_depth = self.right_child.get_tree_depth() if self.right_child else 0
        
        return 1 + max(left_depth, right_depth)
    
    def count_nodes(self) -> int:
        """
        Count the total number of nodes in the subtree rooted at this node.
        
        Returns:
            int: Total number of nodes (including this one).
        """
        count = 1
        if self.left_child:
            count += self.left_child.count_nodes()
        if self.right_child:
            count += self.right_child.count_nodes()
        return count
    
    def count_leaves(self) -> int:
        """
        Count the number of leaf nodes in the subtree rooted at this node.
        
        Returns:
            int: Number of leaf nodes.
        """
        if self.is_leaf:
            return 1
        
        count = 0
        if self.left_child:
            count += self.left_child.count_leaves()
        if self.right_child:
            count += self.right_child.count_leaves()
        return count
