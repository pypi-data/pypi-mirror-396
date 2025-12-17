"""
OC1 Logging Module - Task 3

This module provides detailed logging for tree construction, including:
- Hyperplane coefficients at each node
- Random seeds used
- Impurity values
- Split decisions
- Pruning operations

Paper Reference: Section 2 - Tree construction process
"""

import logging
from typing import Optional, Dict, Any, List
import numpy as np
from datetime import datetime


class TreeConstructionLogger:
    """
    Logger for OC1 tree construction process.
    
    Task 3: Provides detailed logging of:
    - Node creation and splitting decisions
    - Hyperplane coefficients and random seeds
    - Impurity values and stopping criteria
    - Pruning operations
    """
    
    def __init__(
        self,
        log_level: int = logging.INFO,
        log_file: Optional[str] = None,
        verbose: bool = True,
    ):
        """
        Initialize the tree construction logger.
        
        Args:
            log_level: Python logging level (logging.DEBUG, INFO, WARNING, ERROR).
            log_file: Optional file path to write logs to.
            verbose: Whether to print logs to console.
        """
        self.logger = logging.getLogger("OC1.TreeConstruction")
        self.logger.setLevel(log_level)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Console handler
        if verbose:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file, mode='w')  # Explicitly set mode to 'w'
            file_handler.setLevel(log_level)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self._file_handler = file_handler  # Store reference for cleanup
        else:
            self._file_handler = None
        
        self.construction_log: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
    
    def log_tree_start(self, n_samples: int, n_features: int, random_state: Optional[int]) -> None:
        """Log the start of tree construction."""
        self.start_time = datetime.now()
        self.logger.info("=" * 60)
        self.logger.info("Starting OC1 Tree Construction")
        self.logger.info("=" * 60)
        self.logger.info(f"Dataset: {n_samples} samples, {n_features} features")
        self.logger.info(f"Random state: {random_state}")
        self.logger.info(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("")
    
    def log_node_creation(
        self,
        depth: int,
        n_samples: int,
        class_distribution: Dict[Any, int],
        is_leaf: bool,
        reason: Optional[str] = None,
    ) -> None:
        """Log the creation of a node."""
        indent = "  " * depth
        node_type = "Leaf" if is_leaf else "Internal"
        
        self.logger.info(f"{indent}[Depth {depth}] Creating {node_type} Node")
        self.logger.info(f"{indent}  Samples: {n_samples}")
        self.logger.info(f"{indent}  Class distribution: {class_distribution}")
        
        if reason:
            self.logger.info(f"{indent}  Reason: {reason}")
        
        self.construction_log.append({
            'event': 'node_creation',
            'depth': depth,
            'n_samples': n_samples,
            'class_distribution': class_distribution,
            'is_leaf': is_leaf,
            'reason': reason,
        })
    
    def log_hyperplane_search(
        self,
        depth: int,
        n_restarts: int,
        random_seed: int,
        initial_method: str,
    ) -> None:
        """Log the start of hyperplane search."""
        indent = "  " * depth
        self.logger.info(f"{indent}Searching for best hyperplane:")
        self.logger.info(f"{indent}  Restarts: {n_restarts}")
        self.logger.info(f"{indent}  Random seed: {random_seed}")
        self.logger.info(f"{indent}  Initial method: {initial_method}")
        
        self.construction_log.append({
            'event': 'hyperplane_search_start',
            'depth': depth,
            'n_restarts': n_restarts,
            'random_seed': random_seed,
            'initial_method': initial_method,
        })
    
    def log_hyperplane_found(
        self,
        depth: int,
        hyperplane: np.ndarray,
        impurity: float,
        impurity_measure: str,
        n_iterations: Optional[int] = None,
    ) -> None:
        """Log the hyperplane found for a node."""
        indent = "  " * depth
        coef_str = ", ".join([f"{c:.6f}" for c in hyperplane])
        
        self.logger.info(f"{indent}Best hyperplane found:")
        self.logger.info(f"{indent}  Coefficients: [{coef_str}]")
        self.logger.info(f"{indent}  Impurity ({impurity_measure.upper()}): {impurity:.6f}")
        if n_iterations is not None:
            self.logger.info(f"{indent}  Iterations: {n_iterations}")
        
        self.construction_log.append({
            'event': 'hyperplane_found',
            'depth': depth,
            'hyperplane': hyperplane.copy(),
            'impurity': impurity,
            'impurity_measure': impurity_measure,
            'n_iterations': n_iterations,
        })
    
    def log_split_decision(
        self,
        depth: int,
        n_left: int,
        n_right: int,
        impurity_left: Optional[float] = None,
        impurity_right: Optional[float] = None,
    ) -> None:
        """Log the decision to split a node."""
        indent = "  " * depth
        self.logger.info(f"{indent}Splitting node:")
        self.logger.info(f"{indent}  Left child: {n_left} samples")
        self.logger.info(f"{indent}  Right child: {n_right} samples")
        if impurity_left is not None:
            self.logger.info(f"{indent}  Left impurity: {impurity_left:.6f}")
        if impurity_right is not None:
            self.logger.info(f"{indent}  Right impurity: {impurity_right:.6f}")
        
        self.construction_log.append({
            'event': 'split_decision',
            'depth': depth,
            'n_left': n_left,
            'n_right': n_right,
            'impurity_left': impurity_left,
            'impurity_right': impurity_right,
        })
    
    def log_stopping_criterion(
        self,
        depth: int,
        criterion: str,
        value: Any,
    ) -> None:
        """Log why a node was not split."""
        indent = "  " * depth
        self.logger.info(f"{indent}Stopping criterion met: {criterion} = {value}")
        
        self.construction_log.append({
            'event': 'stopping_criterion',
            'depth': depth,
            'criterion': criterion,
            'value': value,
        })
    
    def log_tree_complete(
        self,
        n_nodes: int,
        n_leaves: int,
        max_depth: int,
    ) -> None:
        """Log the completion of tree construction."""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
        else:
            duration = 0.0
        
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("Tree Construction Complete")
        self.logger.info("=" * 60)
        self.logger.info(f"Total nodes: {n_nodes}")
        self.logger.info(f"Leaf nodes: {n_leaves}")
        self.logger.info(f"Max depth: {max_depth}")
        self.logger.info(f"Construction time: {duration:.3f} seconds")
        self.logger.info("=" * 60)
        
        self.construction_log.append({
            'event': 'tree_complete',
            'n_nodes': n_nodes,
            'n_leaves': n_leaves,
            'max_depth': max_depth,
            'duration': duration,
        })
    
    def log_pruning(
        self,
        method: str,
        n_nodes_pruned: int,
        n_leaves_before: int,
        n_leaves_after: int,
    ) -> None:
        """Log pruning operation."""
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info(f"Pruning Tree (method: {method})")
        self.logger.info("=" * 60)
        self.logger.info(f"Nodes pruned: {n_nodes_pruned}")
        self.logger.info(f"Leaves before: {n_leaves_before}")
        self.logger.info(f"Leaves after: {n_leaves_after}")
        self.logger.info("=" * 60)
        
        self.construction_log.append({
            'event': 'pruning',
            'method': method,
            'n_nodes_pruned': n_nodes_pruned,
            'n_leaves_before': n_leaves_before,
            'n_leaves_after': n_leaves_after,
        })
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get a summary of the construction log."""
        return {
            'total_events': len(self.construction_log),
            'nodes_created': sum(1 for e in self.construction_log if e['event'] == 'node_creation'),
            'hyperplanes_found': sum(1 for e in self.construction_log if e['event'] == 'hyperplane_found'),
            'splits': sum(1 for e in self.construction_log if e['event'] == 'split_decision'),
            'construction_log': self.construction_log,
        }
    
    def close(self) -> None:
        """Close all handlers and release file handles."""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


def get_default_logger(verbose: bool = True) -> TreeConstructionLogger:
    """Get a default logger instance."""
    return TreeConstructionLogger(verbose=verbose)

