"""
OC1 Oblique Decision Tree Classifier

This module implements the main ObliqueDecisionTree class as specified in the OC1 paper
"OC1: A randomized algorithm for building oblique decision trees" by Murthy et al. (1992).

Paper Reference:
- Section 2: Recursive tree construction algorithm
- Section 2.1: Hill-climbing for hyperplane optimization
- Section 2.4: Stopping criteria (zero impurity)

Key Features:
- Recursive tree construction with oblique hyperplane splits
- Deterministic hill-climbing optimization (Task 1)
- Multi-class classification support
- Compatible with Task 2 (randomization) and Task 3 (pruning) extensions
- Export methods: to_dict(), to_json(), to_dot()
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import json
import warnings

from oc1.core.node import ObliqueTreeNode
from oc1.core.splits import (
    partition_data,
    calculate_impurity_from_partition,
    compute_class_counts,
    is_pure,
    get_majority_class,
)
from oc1.core.hill_climb import (
    hill_climb,
    find_best_hyperplane,
    initialize_hyperplane,
)
from oc1.core.logging import TreeConstructionLogger, get_default_logger


class ObliqueDecisionTree:
    """
    Oblique Decision Tree Classifier implementing the OC1 algorithm.
    
    This classifier builds a decision tree where each internal node contains
    an oblique hyperplane that splits the feature space. Unlike axis-parallel
    decision trees (like CART or C4.5), oblique trees can represent linear
    decision boundaries at any angle.
    
    Hyperplane equation at each node:
        ∑_{i=1}^{d} (a_i * x_i) + a_{d+1} = 0
    
    Partitioning rule (Section 2):
        - Left child: V_j > 0
        - Right child: V_j ≤ 0
        where V_j = ∑(a_i * x_j^i) + a_{d+1}
    
    Attributes:
        root: Root node of the tree (ObliqueTreeNode)
        n_features: Number of features in training data
        classes_: Unique class labels
        max_depth: Maximum tree depth
        min_samples_leaf: Minimum samples required in a leaf
        min_samples_split: Minimum samples required to split a node
        impurity_measure: "sm" (Sum Minority) or "mm" (Max Minority)
        max_iterations: Maximum hill-climbing iterations
        n_restarts: Number of random restarts (1 for deterministic)
        random_state: Random seed for reproducibility
    
    Paper Reference: Murthy et al., AAAI-1992
    
    Example:
        >>> from oc1.core.tree import ObliqueDecisionTree
        >>> import numpy as np
        >>> X = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        >>> y = np.array([0, 1, 1, 0])
        >>> tree = ObliqueDecisionTree(max_depth=3)
        >>> tree.fit(X, y)
        >>> tree.predict(X)
    """
    
    def __init__(
        self,
        max_depth: Optional[int] = None,
        min_samples_leaf: int = 1,
        min_samples_split: int = 2,
        impurity_measure: str = "sm",
        max_iterations: int = 100,
        n_restarts: int = 10,
        random_state: Optional[int] = None,
        impurity_threshold: float = 0.0,
        verbose: bool = False,
        log_file: Optional[str] = None,
    ) -> None:
        """
        Initialize the Oblique Decision Tree classifier.
        
        Args:
            max_depth: Maximum depth of the tree. None for unlimited.
            min_samples_leaf: Minimum number of samples required in a leaf node.
            min_samples_split: Minimum number of samples required to split a node.
            impurity_measure: "sm" for Sum Minority or "mm" for Max Minority.
            max_iterations: Maximum number of hill-climbing iterations per node.
            n_restarts: Number of random restarts for hill-climbing.
                       Use 1 for deterministic (Task 1), >1 for randomized (Task 2).
            random_state: Random seed for reproducibility.
            impurity_threshold: Stop splitting if impurity falls below this.
                               Prepared for Task 3 pruning integration.
            verbose: Whether to enable verbose logging during tree construction.
            log_file: Optional file path to write detailed logs to.
        
        Paper Reference: Section 2.4 - Stopping criteria
        """
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.min_samples_split = min_samples_split
        self.impurity_measure = impurity_measure.lower()
        self.max_iterations = max_iterations
        self.n_restarts = n_restarts
        self.random_state = random_state
        self.impurity_threshold = impurity_threshold
        self.verbose = verbose
        self.log_file = log_file
        
        # Validate parameters
        self._validate_params()
        
        # Tree state (set after fit)
        self.root: Optional[ObliqueTreeNode] = None
        self.n_features_: int = 0
        self.classes_: np.ndarray = np.array([])
        self.n_classes_: int = 0
        self._is_fitted: bool = False
        
        # Task 3: Logging support
        self.logger: Optional[TreeConstructionLogger] = None
        self.verbose: bool = verbose
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'ObliqueDecisionTree':
        """
        Build the oblique decision tree from training data.
        
        Args:
            X: Training feature matrix of shape (n_samples, n_features).
            y: Training labels of shape (n_samples,).
        
        Returns:
            self: The fitted classifier.
        
        Raises:
            ValueError: If X and y have inconsistent shapes.
        
        Paper Reference: Section 2 - Recursive tree construction
        """
        # Input validation
        X = np.atleast_2d(X).astype(np.float64)
        y = np.atleast_1d(y)
        
        if len(X) != len(y):
            raise ValueError(f"X has {len(X)} samples but y has {len(y)}")
        
        if len(X) == 0:
            raise ValueError("Cannot fit on empty dataset")
        
        # Set random state using modern RNG
        if self.random_state is not None:
            self._rng = np.random.default_rng(self.random_state)
        else:
            self._rng = np.random.default_rng()
        
        # Store dataset info
        self.n_features_ = X.shape[1]
        self.classes_ = np.unique(y)
        self.n_classes_ = len(self.classes_)
        
        # Task 3: Initialize logger (always, but may be silent if verbose=False and no log_file)
        self.logger = TreeConstructionLogger(
            verbose=self.verbose,
            log_file=self.log_file,
        )
        self.logger.log_tree_start(
            n_samples=len(X),
            n_features=self.n_features_,
            random_state=self.random_state,
        )
        
        # Build tree recursively
        self.root = self._build_tree(X, y, depth=0)
        self._is_fitted = True
        
        # Task 3: Log completion
        if self.logger:
            self.logger.log_tree_complete(
                n_nodes=self.get_n_nodes(),
                n_leaves=self.get_n_leaves(),
                max_depth=self.get_depth(),
            )
        
        return self
    
    def _build_tree(
        self,
        X: np.ndarray,
        y: np.ndarray,
        depth: int,
        parent: Optional[ObliqueTreeNode] = None,
    ) -> ObliqueTreeNode:
        """
        Recursively build the decision tree.
        
        This implements the recursive tree construction algorithm:
        1. Check stopping criteria (pure node, min samples, max depth)
        2. Find best hyperplane using hill-climbing
        3. Partition data and recursively build children
        
        Args:
            X: Feature matrix for current node.
            y: Labels for current node.
            depth: Current depth in the tree.
            parent: Parent node reference (for Task 3 pruning support).
        
        Returns:
            ObliqueTreeNode: The constructed node (may be leaf or internal).
        
        Paper Reference: Section 2 - Recursive algorithm
        """
        n_samples = len(y)
        class_counts = compute_class_counts(y)
        majority_class = get_majority_class(y)
        
        # Create node with parent reference
        node = ObliqueTreeNode(
            class_distribution=class_counts,
            depth=depth,
            n_samples=n_samples,
            predicted_class=majority_class,
            parent=parent,
        )
        
        # Task 3: Log node creation
        if self.logger:
            self.logger.log_node_creation(
                depth=depth,
                n_samples=n_samples,
                class_distribution=class_counts,
                is_leaf=False,
            )
        
        # Check stopping criteria (Section 2.4)
        should_stop = False
        stop_reason = None
        
        if is_pure(y):  # Zero impurity
            should_stop = True
            stop_reason = "Zero impurity (pure node)"
        elif n_samples < self.min_samples_split:
            should_stop = True
            stop_reason = f"n_samples ({n_samples}) < min_samples_split ({self.min_samples_split})"
        elif n_samples < 2 * self.min_samples_leaf:
            should_stop = True
            stop_reason = f"n_samples ({n_samples}) < 2 * min_samples_leaf ({2 * self.min_samples_leaf})"
        elif self.max_depth is not None and depth >= self.max_depth:
            should_stop = True
            stop_reason = f"depth ({depth}) >= max_depth ({self.max_depth})"
        
        if should_stop:
            node.is_leaf = True
            if self.logger:
                self.logger.log_stopping_criterion(depth, stop_reason, None)
                self.logger.log_node_creation(
                    depth=depth,
                    n_samples=n_samples,
                    class_distribution=class_counts,
                    is_leaf=True,
                    reason=stop_reason,
                )
            return node
        
        # Find best hyperplane using hill-climbing (Section 2.1)
        # Generate a seed from tree's RNG for reproducibility
        node_seed = int(self._rng.integers(0, 2**31 - 1))
        
        # Task 3: Log hyperplane search
        if self.logger:
            self.logger.log_hyperplane_search(
                depth=depth,
                n_restarts=self.n_restarts,
                random_seed=node_seed,
                initial_method="axis_parallel" if self.n_restarts == 1 else "random",
            )
        
        try:
            best_hyperplane, best_impurity = find_best_hyperplane(
                X, y,
                impurity_measure=self.impurity_measure,
                n_restarts=self.n_restarts,
                max_iterations=self.max_iterations,
                random_state=node_seed,
                use_random_perturbation_order=True,  # Task 2: Enable random perturbation order
            )
            
            # Task 3: Log hyperplane found
            if self.logger:
                self.logger.log_hyperplane_found(
                    depth=depth,
                    hyperplane=best_hyperplane,
                    impurity=best_impurity,
                    impurity_measure=self.impurity_measure,
                )
        except Exception as e:
            # Fall back to leaf if hyperplane finding fails
            node.is_leaf = True
            if self.logger:
                self.logger.log_stopping_criterion(
                    depth, "Hyperplane search failed", str(e)
                )
            return node
        
        # Check if split is useful (impurity threshold for Task 3)
        if best_impurity <= self.impurity_threshold:
            node.is_leaf = True
            node.impurity = best_impurity
            if self.logger:
                self.logger.log_stopping_criterion(
                    depth, "Impurity threshold", f"{best_impurity:.6f} <= {self.impurity_threshold}"
                )
            return node
        
        # Partition data
        X_left, y_left, X_right, y_right, _ = partition_data(X, y, best_hyperplane)
        
        # Task 3: Log split decision
        if self.logger:
            from oc1.core.splits import calculate_impurity_from_partition
            sm_left, mm_left = calculate_impurity_from_partition(y_left, np.array([]))
            sm_right, mm_right = calculate_impurity_from_partition(y_right, np.array([]))
            impurity_left = sm_left if self.impurity_measure == "sm" else mm_left
            impurity_right = sm_right if self.impurity_measure == "sm" else mm_right
            
            self.logger.log_split_decision(
                depth=depth,
                n_left=len(y_left),
                n_right=len(y_right),
                impurity_left=impurity_left if len(y_left) > 0 else None,
                impurity_right=impurity_right if len(y_right) > 0 else None,
            )
        
        # Check if partition is valid
        if len(y_left) < self.min_samples_leaf or len(y_right) < self.min_samples_leaf:
            node.is_leaf = True
            if self.logger:
                self.logger.log_stopping_criterion(
                    depth, "Insufficient samples in partition",
                    f"left={len(y_left)}, right={len(y_right)}, min={self.min_samples_leaf}"
                )
            return node
        
        # Check for degenerate split (all to one side)
        if len(y_left) == 0 or len(y_right) == 0:
            node.is_leaf = True
            if self.logger:
                self.logger.log_stopping_criterion(
                    depth, "Degenerate split", f"left={len(y_left)}, right={len(y_right)}"
                )
            return node
        
        # Set hyperplane and create internal node
        node.hyperplane = best_hyperplane
        node.impurity = best_impurity
        node.is_leaf = False
        
        # Recursively build children with parent reference
        node.left_child = self._build_tree(X_left, y_left, depth + 1, parent=node)
        node.right_child = self._build_tree(X_right, y_right, depth + 1, parent=node)
        
        return node
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels for samples in X.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Predicted class labels of shape (n_samples,).
        
        Raises:
            ValueError: If the tree has not been fitted.
        """
        self._check_is_fitted()
        
        X = np.atleast_2d(X)
        
        if X.shape[1] != self.n_features_:
            raise ValueError(
                f"X has {X.shape[1]} features but tree was trained with "
                f"{self.n_features_} features"
            )
        
        predictions = np.array([
            self.root.predict_single(x) for x in X
        ])
        
        return predictions
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities for samples in X.
        
        Probabilities are based on the class distribution in the leaf node.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Class probabilities of shape (n_samples, n_classes).
        """
        self._check_is_fitted()
        
        X = np.atleast_2d(X)
        n_samples = X.shape[0]
        
        probabilities = np.zeros((n_samples, self.n_classes_))
        
        for i, x in enumerate(X):
            leaf = self._get_leaf(x)
            total = sum(leaf.class_distribution.values())
            
            for j, cls in enumerate(self.classes_):
                count = leaf.class_distribution.get(cls, 0)
                probabilities[i, j] = count / total if total > 0 else 0
        
        return probabilities
    
    def _get_leaf(self, x: np.ndarray) -> ObliqueTreeNode:
        """
        Get the leaf node for a single sample.
        
        Args:
            x: Feature vector of shape (n_features,).
        
        Returns:
            ObliqueTreeNode: The leaf node reached by the sample.
        """
        node = self.root
        
        while not node.is_leaf:
            x = np.atleast_1d(x)
            V = node.evaluate(x.reshape(1, -1))[0]
            
            if V > 0:
                node = node.left_child if node.left_child else node
            else:
                node = node.right_child if node.right_child else node
        
        return node
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Calculate the accuracy of the classifier.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features).
            y: True class labels of shape (n_samples,).
        
        Returns:
            float: Accuracy score (proportion of correct predictions).
        """
        predictions = self.predict(X)
        return np.mean(predictions == y)
    
    def get_depth(self) -> int:
        """
        Get the maximum depth of the tree.
        
        Returns:
            int: Maximum depth (0 if tree is just a leaf).
        """
        self._check_is_fitted()
        return self.root.get_tree_depth()
    
    def get_n_leaves(self) -> int:
        """
        Get the number of leaf nodes in the tree.
        
        Returns:
            int: Number of leaves.
        """
        self._check_is_fitted()
        return self.root.count_leaves()
    
    def get_n_nodes(self) -> int:
        """
        Get the total number of nodes in the tree.
        
        Returns:
            int: Total number of nodes.
        """
        self._check_is_fitted()
        return self.root.count_nodes()
    
    def get_all_nodes(self) -> List[ObliqueTreeNode]:
        """
        Get all nodes in the tree in breadth-first order.
        
        This method is useful for Task 3 pruning operations that need
        to traverse or inspect all nodes in the tree.
        
        Returns:
            List[ObliqueTreeNode]: All nodes in breadth-first order.
        
        Example:
            >>> tree.fit(X, y)
            >>> nodes = tree.get_all_nodes()
            >>> leaves = [n for n in nodes if n.is_leaf]
        """
        self._check_is_fitted()
        
        nodes = []
        queue = [self.root]
        
        while queue:
            node = queue.pop(0)
            nodes.append(node)
            
            if node.left_child:
                queue.append(node.left_child)
            if node.right_child:
                queue.append(node.right_child)
        
        return nodes
    
    def prune(
        self,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        method: str = "rep",
        impurity_threshold: Optional[float] = None,
    ) -> 'ObliqueDecisionTree':
        """
        Prune the tree to reduce overfitting.
        
        Task 3: Implements subtree pruning based on impurity threshold or validation set.
        
        Pruning methods:
        - "rep": Reduced Error Pruning - prune subtrees that don't improve
                 validation accuracy
        - "impurity": Prune subtrees where impurity is below threshold
        - "cost_complexity": Cost-complexity pruning (CART-style) - not yet implemented
        
        Args:
            X_val: Validation feature matrix for pruning decisions (required for "rep").
            y_val: Validation labels (required for "rep").
            method: Pruning method to use ("rep", "impurity", "cost_complexity").
            impurity_threshold: Impurity threshold for "impurity" method.
                               If None, uses self.impurity_threshold.
        
        Returns:
            self: The pruned tree.
        
        Paper Reference: Section 2.4 - Pruning based on impurity threshold
        """
        self._check_is_fitted()
        
        if method == "impurity":
            threshold = impurity_threshold if impurity_threshold is not None else self.impurity_threshold
            n_leaves_before = self.get_n_leaves()
            n_pruned = self._prune_by_impurity(self.root, threshold)
            n_leaves_after = self.get_n_leaves()
            
            # Log pruning if logger is available
            if self.logger:
                self.logger.log_pruning(
                    method="impurity",
                    n_nodes_pruned=n_pruned,
                    n_leaves_before=n_leaves_before,
                    n_leaves_after=n_leaves_after,
                )
        elif method == "rep":
            if X_val is None or y_val is None:
                raise ValueError("X_val and y_val are required for Reduced Error Pruning")
            self._prune_reduced_error(X_val, y_val)
        elif method == "cost_complexity":
            raise NotImplementedError("Cost-complexity pruning not yet implemented")
        else:
            raise ValueError(f"Unknown pruning method: {method}")
        
        return self
    
    def _prune_by_impurity(
        self,
        node: ObliqueTreeNode,
        threshold: float,
    ) -> int:
        """
        Prune subtrees where impurity is below threshold.
        
        Task 3: Recursively prune nodes whose impurity is below the threshold,
        converting them to leaf nodes.
        
        Args:
            node: Current node to check for pruning.
            threshold: Impurity threshold below which to prune.
        
        Returns:
            Number of nodes pruned in this subtree.
        """
        if node.is_leaf:
            return 0
        
        n_pruned = 0
        
        # Recursively prune children first (bottom-up)
        if node.left_child:
            n_pruned += self._prune_by_impurity(node.left_child, threshold)
        if node.right_child:
            n_pruned += self._prune_by_impurity(node.right_child, threshold)
        
        # Check if this node should be pruned
        if node.impurity <= threshold:
            # Convert to leaf node
            node.is_leaf = True
            node.hyperplane = None
            node.left_child = None
            node.right_child = None
            n_pruned += 1
        
        return n_pruned
    
    def _prune_reduced_error(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray,
    ) -> None:
        """
        Reduced Error Pruning: prune subtrees that don't improve validation accuracy.
        
        Task 3: Bottom-up pruning where a subtree is pruned if the leaf node
        performs as well or better on the validation set.
        
        Args:
            X_val: Validation feature matrix.
            y_val: Validation labels.
        """
        # Get all nodes in bottom-up order (leaves to root)
        nodes = self._get_nodes_bottom_up()
        n_pruned = 0
        
        for node in nodes:
            if node.is_leaf:
                continue
            
            # Get validation samples that reach this node
            val_indices = self._get_samples_reaching_node(X_val, node)
            if len(val_indices) == 0:
                continue
            
            X_node = X_val[val_indices]
            y_node = y_val[val_indices]
            
            # Accuracy with subtree
            subtree_accuracy = self._evaluate_node_accuracy(X_node, y_node, node)
            
            # Accuracy if pruned to leaf
            leaf_accuracy = np.mean(
                np.array([node.predicted_class] * len(y_node)) == y_node
            )
            
            # Prune if leaf performs as well or better
            if leaf_accuracy >= subtree_accuracy:
                node.is_leaf = True
                node.hyperplane = None
                node.left_child = None
                node.right_child = None
                n_pruned += 1
        
        # Log pruning if logger is available
        if self.logger:
            n_leaves_before = sum(1 for n in nodes if n.is_leaf)
            n_leaves_after = self.get_n_leaves()
            self.logger.log_pruning(
                method="rep",
                n_nodes_pruned=n_pruned,
                n_leaves_before=n_leaves_before,
                n_leaves_after=n_leaves_after,
            )
    
    def _get_nodes_bottom_up(self) -> List[ObliqueTreeNode]:
        """Get all nodes in bottom-up order (leaves first, root last)."""
        all_nodes = self.get_all_nodes()
        # Sort by depth descending (deepest first)
        return sorted(all_nodes, key=lambda n: n.depth, reverse=True)
    
    def _get_samples_reaching_node(
        self,
        X: np.ndarray,
        target_node: ObliqueTreeNode,
    ) -> np.ndarray:
        """Get indices of samples that reach the target node."""
        indices = []
        
        for i, x in enumerate(X):
            node = self.root
            path = []
            
            # Traverse to find path to target
            while node is not None and node != target_node:
                path.append(node)
                if node.is_leaf:
                    break
                V = node.evaluate(x.reshape(1, -1))[0]
                if V > 0:
                    node = node.left_child
                else:
                    node = node.right_child
            
            if node == target_node:
                indices.append(i)
        
        return np.array(indices)
    
    def _evaluate_node_accuracy(
        self,
        X: np.ndarray,
        y: np.ndarray,
        node: ObliqueTreeNode,
    ) -> float:
        """Evaluate accuracy of predictions from a subtree rooted at node."""
        if node.is_leaf:
            predictions = np.array([node.predicted_class] * len(y))
            return np.mean(predictions == y)
        
        # Traverse subtree for each sample
        predictions = []
        for x in X:
            pred = self._predict_from_node(x, node)
            predictions.append(pred)
        
        return np.mean(np.array(predictions) == y)
    
    def _predict_from_node(
        self,
        x: np.ndarray,
        node: ObliqueTreeNode,
    ) -> Any:
        """Predict class for a sample starting from a given node."""
        if node.is_leaf:
            return node.predicted_class
        
        x = np.atleast_1d(x)
        V = node.evaluate(x.reshape(1, -1))[0]
        
        if V > 0:
            if node.left_child:
                return self._predict_from_node(x, node.left_child)
            return node.predicted_class
        else:
            if node.right_child:
                return self._predict_from_node(x, node.right_child)
            return node.predicted_class
    
    def _check_is_fitted(self) -> None:
        """Check if the tree has been fitted."""
        if not self._is_fitted or self.root is None:
            raise ValueError(
                "This ObliqueDecisionTree instance is not fitted yet. "
                "Call 'fit' with appropriate arguments before using this method."
            )
    
    def get_hyperplanes(self) -> List[Tuple[np.ndarray, int]]:
        """
        Get all hyperplanes in the tree with their depths.
        
        Returns:
            List of (hyperplane, depth) tuples for all internal nodes.
        """
        self._check_is_fitted()
        
        hyperplanes = []
        self._collect_hyperplanes(self.root, hyperplanes)
        return hyperplanes
    
    def _collect_hyperplanes(
        self,
        node: ObliqueTreeNode,
        hyperplanes: List[Tuple[np.ndarray, int]],
    ) -> None:
        """Recursively collect hyperplanes from the tree."""
        if node is None or node.is_leaf:
            return
        
        if node.hyperplane is not None:
            hyperplanes.append((node.hyperplane.copy(), node.depth))
        
        self._collect_hyperplanes(node.left_child, hyperplanes)
        self._collect_hyperplanes(node.right_child, hyperplanes)
    
    def print_tree(self, feature_names: Optional[List[str]] = None) -> str:
        """
        Generate a string representation of the tree structure.
        
        Args:
            feature_names: Optional list of feature names for readable output.
        
        Returns:
            str: Formatted tree structure.
        """
        self._check_is_fitted()
        
        if feature_names is None:
            feature_names = [f"x{i}" for i in range(self.n_features_)]
        
        lines = []
        self._print_node(self.root, "", True, feature_names, lines)
        return "\n".join(lines)
    
    def _print_node(
        self,
        node: ObliqueTreeNode,
        prefix: str,
        is_last: bool,
        feature_names: List[str],
        lines: List[str],
    ) -> None:
        """Recursively print node information."""
        connector = "└── " if is_last else "├── "
        
        if node.is_leaf:
            lines.append(
                f"{prefix}{connector}Leaf: class={node.predicted_class}, "
                f"samples={node.n_samples}, dist={node.class_distribution}"
            )
        else:
            # Format hyperplane equation
            terms = []
            for i, coef in enumerate(node.hyperplane[:-1]):
                if abs(coef) > 1e-10:
                    sign = "+" if coef > 0 else "-"
                    terms.append(f"{sign}{abs(coef):.3f}*{feature_names[i]}")
            
            bias = node.hyperplane[-1]
            bias_str = f"{'+' if bias >= 0 else '-'}{abs(bias):.3f}"
            equation = "".join(terms) + bias_str
            
            lines.append(
                f"{prefix}{connector}Split: {equation} = 0, "
                f"samples={node.n_samples}, impurity={node.impurity:.3f}"
            )
            
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            if node.left_child:
                self._print_node(
                    node.left_child, new_prefix, node.right_child is None,
                    feature_names, lines
                )
            if node.right_child:
                self._print_node(
                    node.right_child, new_prefix, True,
                    feature_names, lines
                )
    
    def __repr__(self) -> str:
        """String representation of the tree."""
        if self._is_fitted:
            return (
                f"ObliqueDecisionTree(depth={self.get_depth()}, "
                f"n_leaves={self.get_n_leaves()}, "
                f"impurity='{self.impurity_measure}')"
            )
        else:
            return "ObliqueDecisionTree(not fitted)"

    # ==================== NEW: Export Methods ====================
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export tree structure to a dictionary.
        
        Returns:
            Dict containing complete tree structure and metadata.
        
        Example:
            >>> tree.fit(X, y)
            >>> tree_dict = tree.to_dict()
            >>> # Can be serialized with json.dumps(tree_dict)
        """
        self._check_is_fitted()
        
        return {
            "metadata": {
                "n_features": self.n_features_,
                "n_classes": self.n_classes_,
                "classes": self.classes_.tolist(),
                "max_depth": self.max_depth,
                "min_samples_leaf": self.min_samples_leaf,
                "impurity_measure": self.impurity_measure,
                "n_restarts": self.n_restarts,
            },
            "tree_stats": {
                "depth": self.get_depth(),
                "n_nodes": self.get_n_nodes(),
                "n_leaves": self.get_n_leaves(),
            },
            "root": self._node_to_dict(self.root),
        }
    
    def _node_to_dict(self, node: ObliqueTreeNode) -> Dict[str, Any]:
        """Convert a node and its subtree to dictionary."""
        if node is None:
            return None
        
        node_dict = {
            "is_leaf": node.is_leaf,
            "depth": node.depth,
            "n_samples": node.n_samples,
            "impurity": node.impurity,
            "predicted_class": node.predicted_class,
            "class_distribution": {str(k): v for k, v in node.class_distribution.items()},
        }
        
        if not node.is_leaf and node.hyperplane is not None:
            node_dict["hyperplane"] = node.hyperplane.tolist()
            node_dict["left_child"] = self._node_to_dict(node.left_child)
            node_dict["right_child"] = self._node_to_dict(node.right_child)
        
        return node_dict
    
    def to_json(self, filepath: Optional[str] = None, indent: int = 2) -> str:
        """
        Export tree structure to JSON.
        
        Args:
            filepath: Optional path to save JSON file.
            indent: JSON indentation level.
        
        Returns:
            JSON string representation of the tree.
        
        Example:
            >>> json_str = tree.to_json()
            >>> tree.to_json("model.json")  # Save to file
        """
        tree_dict = self.to_dict()
        json_str = json.dumps(tree_dict, indent=indent, default=str)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
        
        return json_str
    
    def to_dot(self, feature_names: Optional[List[str]] = None) -> str:
        """
        Export tree structure to DOT format for Graphviz visualization.
        
        Args:
            feature_names: Optional list of feature names.
        
        Returns:
            DOT format string.
        
        Example:
            >>> dot_str = tree.to_dot()
            >>> # Render with: graphviz.Source(dot_str).render("tree")
        """
        self._check_is_fitted()
        
        if feature_names is None:
            feature_names = [f"x{i}" for i in range(self.n_features_)]
        
        lines = ["digraph OC1Tree {"]
        lines.append('    node [shape=box, style="rounded,filled"];')
        lines.append('    edge [fontsize=10];')
        
        self._node_to_dot(self.root, lines, feature_names, node_id=[0])
        
        lines.append("}")
        return "\n".join(lines)
    
    def _node_to_dot(
        self,
        node: ObliqueTreeNode,
        lines: List[str],
        feature_names: List[str],
        node_id: List[int],
    ) -> int:
        """Recursively convert nodes to DOT format."""
        current_id = node_id[0]
        node_id[0] += 1
        
        if node.is_leaf:
            color = "#98FB98" if node.n_samples > 0 else "#FFFFFF"
            label = f"class={node.predicted_class}\\nsamples={node.n_samples}"
            lines.append(f'    node{current_id} [label="{label}", fillcolor="{color}"];')
        else:
            # Format hyperplane equation
            terms = []
            for i, coef in enumerate(node.hyperplane[:-1]):
                if abs(coef) > 0.01:
                    terms.append(f"{coef:.2f}*{feature_names[i]}")
            equation = " + ".join(terms) + f" + {node.hyperplane[-1]:.2f}"
            
            color = "#ADD8E6"
            label = f"{equation}\\nsamples={node.n_samples}\\nimp={node.impurity:.3f}"
            lines.append(f'    node{current_id} [label="{label}", fillcolor="{color}"];')
            
            if node.left_child:
                left_id = self._node_to_dot(node.left_child, lines, feature_names, node_id)
                lines.append(f'    node{current_id} -> node{left_id} [label="V > 0"];')
            
            if node.right_child:
                right_id = self._node_to_dot(node.right_child, lines, feature_names, node_id)
                lines.append(f'    node{current_id} -> node{right_id} [label="V ≤ 0"];')
        
        return current_id
    
    # ==================== NEW: Feature Importances ====================
    
    @property
    def feature_importances_(self) -> np.ndarray:
        """
        Compute feature importances based on hyperplane coefficients.
        
        Importances are computed as the sum of absolute coefficient values
        across all hyperplanes, weighted by the number of samples at each node.
        
        Returns:
            np.ndarray: Normalized feature importance scores.
        
        Example:
            >>> tree.fit(X, y)
            >>> importances = tree.feature_importances_
            >>> for i, imp in enumerate(importances):
            ...     print(f"Feature {i}: {imp:.3f}")
        """
        self._check_is_fitted()
        
        importances = np.zeros(self.n_features_)
        total_weight = 0
        
        def accumulate_importances(node: ObliqueTreeNode):
            nonlocal total_weight
            if node is None or node.is_leaf:
                return
            
            if node.hyperplane is not None:
                weight = node.n_samples
                total_weight += weight
                # Add weighted absolute coefficients
                importances[:] += weight * np.abs(node.hyperplane[:-1])
            
            accumulate_importances(node.left_child)
            accumulate_importances(node.right_child)
        
        accumulate_importances(self.root)
        
        # Normalize
        if total_weight > 0:
            importances /= total_weight
        
        # Scale to sum to 1
        if importances.sum() > 0:
            importances /= importances.sum()
        
        return importances
    
    def _validate_params(self) -> None:
        """Validate constructor parameters."""
        if self.max_depth is not None and self.max_depth < 1:
            raise ValueError(f"max_depth must be >= 1, got {self.max_depth}")
        
        if self.min_samples_leaf < 1:
            raise ValueError(f"min_samples_leaf must be >= 1, got {self.min_samples_leaf}")
        
        if self.min_samples_split < 2:
            raise ValueError(f"min_samples_split must be >= 2, got {self.min_samples_split}")
        
        if self.impurity_measure not in ("sm", "mm"):
            raise ValueError(f"impurity_measure must be 'sm' or 'mm', got {self.impurity_measure}")
        
        if self.max_iterations < 1:
            raise ValueError(f"max_iterations must be >= 1, got {self.max_iterations}")
        
        if self.n_restarts < 1:
            raise ValueError(f"n_restarts must be >= 1, got {self.n_restarts}")
        
        if self.impurity_threshold < 0:
            raise ValueError(f"impurity_threshold must be >= 0, got {self.impurity_threshold}")
