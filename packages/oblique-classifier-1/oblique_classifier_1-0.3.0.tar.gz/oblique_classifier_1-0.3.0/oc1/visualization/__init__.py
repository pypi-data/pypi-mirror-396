"""
OC1 Visualization Module - Task 3

This module provides visualization utilities for oblique decision trees.

Components:
- plot_tree: Visualize tree structure
- plot_decision_boundary: Plot 2D decision boundaries
- plot_hyperplanes: Visualize hyperplanes in feature space
"""

from __future__ import annotations
from typing import Optional, List, Tuple, Any, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None  # type: ignore
    patches = None  # type: ignore


def plot_decision_boundary_2d(
    tree,
    X: np.ndarray,
    y: np.ndarray,
    ax: Optional[Any] = None,
    resolution: int = 100,
    alpha: float = 0.3,
    show_data: bool = True,
) -> Optional[Any]:
    """
    Plot 2D decision boundary of an oblique decision tree.
    
    Task 3: Visualizes the decision boundary for 2D datasets by creating
    a grid and coloring regions based on predictions.
    
    Args:
        tree: Fitted ObliqueDecisionTree instance.
        X: Feature matrix of shape (n_samples, 2).
        y: Class labels (optional, for coloring data points).
        ax: Optional matplotlib axes to plot on.
        resolution: Resolution of the decision boundary grid.
        alpha: Transparency of the decision boundary regions.
        show_data: Whether to show the training data points.
    
    Returns:
        matplotlib Figure if ax is None, else None.
    
    Raises:
        ValueError: If tree is not fitted or data is not 2D.
        ImportError: If matplotlib is not installed.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required for visualization. Install with: pip install matplotlib")
    
    if not tree._is_fitted:
        raise ValueError("Tree must be fitted before visualization")
    
    if X.shape[1] != 2:
        raise ValueError(f"plot_decision_boundary_2d requires 2D data, got {X.shape[1]}D")
    
    # Create figure if needed
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    else:
        fig = ax.figure
    
    # Create grid
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, resolution),
        np.linspace(y_min, y_max, resolution)
    )
    
    # Predict for all grid points
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    Z = tree.predict(grid_points)
    Z = Z.reshape(xx.shape)
    
    # Plot decision boundary
    n_classes = len(tree.classes_)
    if n_classes == 2:
        ax.contourf(xx, yy, Z, levels=[0, 0.5, 1], alpha=alpha, colors=['blue', 'red'])
    else:
        ax.contourf(xx, yy, Z, levels=n_classes, alpha=alpha, cmap='viridis')
    
    # Plot data points
    if show_data and y is not None:
        scatter = ax.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis', edgecolors='black', s=50)
        if len(np.unique(y)) <= 10:  # Only show colorbar for reasonable number of classes
            plt.colorbar(scatter, ax=ax, label='Class')
    
    ax.set_xlabel('Feature 1')
    ax.set_ylabel('Feature 2')
    ax.set_title('OC1 Decision Boundary')
    ax.grid(True, alpha=0.3)
    
    return fig if ax is None else None


def plot_hyperplanes_2d(
    tree,
    X: np.ndarray,
    ax: Optional[Any] = None,
    show_data: bool = True,
    colors: Optional[List[str]] = None,
) -> Optional[Any]:
    """
    Plot hyperplanes (decision boundaries) for a 2D oblique tree.
    
    Task 3: Visualizes all hyperplanes in the tree as lines in 2D space.
    
    Args:
        tree: Fitted ObliqueDecisionTree instance.
        X: Feature matrix of shape (n_samples, 2) for determining plot bounds.
        ax: Optional matplotlib axes to plot on.
        show_data: Whether to show the training data points.
        colors: Optional list of colors for hyperplanes.
    
    Returns:
        matplotlib Figure if ax is None, else None.
    
    Raises:
        ValueError: If tree is not fitted or data is not 2D.
        ImportError: If matplotlib is not installed.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required for visualization. Install with: pip install matplotlib")
    
    if not tree._is_fitted:
        raise ValueError("Tree must be fitted before visualization")
    
    if X.shape[1] != 2:
        raise ValueError(f"plot_hyperplanes_2d requires 2D data, got {X.shape[1]}D")
    
    # Create figure if needed
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    else:
        fig = ax.figure
    
    # Get all hyperplanes
    hyperplanes = tree.get_hyperplanes()
    
    if not hyperplanes:
        ax.text(0.5, 0.5, 'No hyperplanes (tree is a single leaf)', 
                ha='center', va='center', transform=ax.transAxes)
        return fig if ax is None else None
    
    # Determine plot bounds
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    
    # Default colors
    if colors is None:
        colors = plt.cm.tab10(np.linspace(0, 1, len(hyperplanes)))
    
    # Plot each hyperplane
    for i, (hyperplane, depth) in enumerate(hyperplanes):
        a, b, c = hyperplane[0], hyperplane[1], hyperplane[2]
        
        # Hyperplane equation: a*x + b*y + c = 0
        # Solve for y: y = (-a*x - c) / b (if b != 0)
        # Or solve for x: x = (-b*y - c) / a (if a != 0)
        
        if abs(b) > 1e-10:
            # Can solve for y
            x_line = np.linspace(x_min, x_max, 100)
            y_line = (-a * x_line - c) / b
            # Clip to plot bounds
            mask = (y_line >= y_min) & (y_line <= y_max)
            ax.plot(x_line[mask], y_line[mask], 
                   color=colors[i % len(colors)], 
                   linewidth=2, 
                   label=f'Depth {depth}',
                   linestyle='--' if depth > 0 else '-')
        elif abs(a) > 1e-10:
            # Can solve for x
            y_line = np.linspace(y_min, y_max, 100)
            x_line = (-b * y_line - c) / a
            # Clip to plot bounds
            mask = (x_line >= x_min) & (x_line <= x_max)
            ax.plot(x_line[mask], y_line[mask],
                   color=colors[i % len(colors)],
                   linewidth=2,
                   label=f'Depth {depth}',
                   linestyle='--' if depth > 0 else '-')
    
    # Plot data points
    if show_data:
        ax.scatter(X[:, 0], X[:, 1], c='black', s=30, alpha=0.5, zorder=10)
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel('Feature 1')
    ax.set_ylabel('Feature 2')
    ax.set_title('OC1 Hyperplanes')
    ax.grid(True, alpha=0.3)
    if len(hyperplanes) <= 10:
        ax.legend(loc='best')
    
    return fig if ax is None else None


def plot_tree_structure(
    tree,
    ax: Optional[Any] = None,
    node_size: int = 1000,
    font_size: int = 10,
) -> Optional[Any]:
    """
    Plot tree structure as a graph.
    
    Task 3: Creates a visual representation of the tree structure.
    
    Args:
        tree: Fitted ObliqueDecisionTree instance.
        ax: Optional matplotlib axes to plot on.
        node_size: Size of nodes in the plot.
        font_size: Font size for node labels.
    
    Returns:
        matplotlib Figure if ax is None, else None.
    
    Raises:
        ValueError: If tree is not fitted.
        ImportError: If matplotlib is not installed.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required for visualization. Install with: pip install matplotlib")
    
    if not tree._is_fitted:
        raise ValueError("Tree must be fitted before visualization")
    
    try:
        import networkx as nx
    except ImportError:
        raise ImportError("networkx is required for tree structure visualization. Install with: pip install networkx")
    
    # Create figure if needed
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 8))
    else:
        fig = ax.figure
    
    # Build graph
    G = nx.DiGraph()
    pos = {}
    labels = {}
    
    def add_node(node, x, y, dx):
        """Recursively add nodes to graph."""
        if node is None:
            return
        
        node_id = id(node)
        
        if node.is_leaf:
            label = f"Leaf\nClass: {node.predicted_class}\nSamples: {node.n_samples}"
            color = 'lightgreen'
        else:
            coef_str = f"{node.hyperplane[0]:.2f}*x1"
            if len(node.hyperplane) > 2:
                coef_str += f" + {node.hyperplane[1]:.2f}*x2"
            if len(node.hyperplane) > 3:
                coef_str += f" + {node.hyperplane[2]:.2f} = 0"
            label = f"Split\n{coef_str}\nSamples: {node.n_samples}"
            color = 'lightblue'
        
        G.add_node(node_id)
        pos[node_id] = (x, y)
        labels[node_id] = label
        
        if not node.is_leaf:
            if node.left_child:
                left_id = add_node(node.left_child, x - dx, y - 1, dx / 2)
                G.add_edge(node_id, left_id, label='> 0')
            if node.right_child:
                right_id = add_node(node.right_child, x + dx, y - 1, dx / 2)
                G.add_edge(node_id, right_id, label='<= 0')
        
        return node_id
    
    # Add root
    add_node(tree.root, 0, 0, 2)
    
    # Draw graph
    node_colors = ['lightgreen' if tree.root.is_leaf else 'lightblue']
    for node_id in G.nodes():
        if node_id != id(tree.root):
            node = None
            # Find node by id (simplified - in practice would need node registry)
            # For now, use color based on depth
            node_colors.append('lightgreen' if len(str(labels[node_id]).split('\n')) > 2 else 'lightblue')
    
    nx.draw(G, pos, ax=ax, with_labels=False, node_color='lightblue',
            node_size=node_size, font_size=font_size, arrows=True)
    
    # Add labels
    for node_id, (x, y) in pos.items():
        ax.text(x, y, labels[node_id], ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
               fontsize=font_size)
    
    ax.set_title('OC1 Tree Structure')
    ax.axis('off')
    
    return fig if ax is None else None


__all__ = [
    "plot_decision_boundary_2d",
    "plot_hyperplanes_2d",
    "plot_tree_structure",
]

