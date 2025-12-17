"""
OC1 Evaluation Module - Task 3

This module provides utilities for model evaluation and cross-validation,
designed for use with OC1 oblique decision trees.

Components:
- cross_validate: K-fold cross-validation for hyperparameter tuning
- stratified_k_fold: Stratified cross-validation for imbalanced datasets
- train_test_split: Utility for splitting data with stratification
- evaluate_classifier: Comprehensive model evaluation metrics
- confusion_matrix: Classification performance analysis
- classification_report: Detailed classification metrics report

Paper Reference: Standard machine learning evaluation practices
"""

from typing import Optional, Tuple, List, Dict, Any, Union
import numpy as np
import time


def train_test_split(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: Optional[int] = None,
    stratify: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split data into training and test sets.
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Labels of shape (n_samples,).
        test_size: Proportion of data to use for testing (0.0 to 1.0).
        random_state: Random seed for reproducibility.
        stratify: Whether to stratify by class labels (maintain class distribution).
    
    Returns:
        Tuple of (X_train, X_test, y_train, y_test).
    
    Example:
        >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    """
    X = np.atleast_2d(X)
    y = np.atleast_1d(y)
    
    if len(X) != len(y):
        raise ValueError(f"X has {len(X)} samples but y has {len(y)}")
    
    if not (0.0 < test_size < 1.0):
        raise ValueError(f"test_size must be between 0 and 1, got {test_size}")
    
    rng = np.random.default_rng(random_state)
    n_samples = len(y)
    n_test = int(n_samples * test_size)
    n_train = n_samples - n_test
    
    if stratify:
        # Stratified split: maintain class distribution
        classes = np.unique(y)
        train_indices = []
        test_indices = []
        
        for cls in classes:
            cls_indices = np.where(y == cls)[0]
            rng.shuffle(cls_indices)
            
            n_test_cls = max(1, int(len(cls_indices) * test_size))
            n_train_cls = len(cls_indices) - n_test_cls
            
            test_indices.extend(cls_indices[:n_test_cls])
            train_indices.extend(cls_indices[n_test_cls:])
        
        # Shuffle final indices
        rng.shuffle(train_indices)
        rng.shuffle(test_indices)
        
        # Ensure we have the right total sizes
        if len(test_indices) > n_test:
            # Remove excess from test
            excess = len(test_indices) - n_test
            train_indices.extend(test_indices[-excess:])
            test_indices = test_indices[:-excess]
        elif len(test_indices) < n_test:
            # Add from train
            needed = n_test - len(test_indices)
            test_indices.extend(train_indices[-needed:])
            train_indices = train_indices[:-needed]
    else:
        # Simple random split
        indices = np.arange(n_samples)
        rng.shuffle(indices)
        test_indices = indices[:n_test]
        train_indices = indices[n_test:]
    
    return X[train_indices], X[test_indices], y[train_indices], y[test_indices]


def confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Compute confusion matrix.
    
    Args:
        y_true: True class labels of shape (n_samples,).
        y_pred: Predicted class labels of shape (n_samples,).
        labels: Optional array of class labels to include. If None, uses all unique labels.
    
    Returns:
        Confusion matrix of shape (n_classes, n_classes).
        Rows represent true classes, columns represent predicted classes.
    
    Example:
        >>> cm = confusion_matrix(y_true, y_pred)
        >>> # cm[i, j] = number of samples with true class i predicted as class j
    """
    y_true = np.atleast_1d(y_true)
    y_pred = np.atleast_1d(y_pred)
    
    if len(y_true) != len(y_pred):
        raise ValueError(f"y_true has {len(y_true)} samples but y_pred has {len(y_pred)}")
    
    if labels is None:
        labels = np.unique(np.concatenate([y_true, y_pred]))
    
    n_classes = len(labels)
    cm = np.zeros((n_classes, n_classes), dtype=int)
    
    # Map labels to indices
    label_to_idx = {label: idx for idx, label in enumerate(labels)}
    
    for true_label, pred_label in zip(y_true, y_pred):
        if true_label in label_to_idx and pred_label in label_to_idx:
            true_idx = label_to_idx[true_label]
            pred_idx = label_to_idx[pred_label]
            cm[true_idx, pred_idx] += 1
    
    return cm


def classification_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[np.ndarray] = None,
    target_names: Optional[List[str]] = None,
) -> str:
    """
    Generate a detailed classification report.
    
    Args:
        y_true: True class labels.
        y_pred: Predicted class labels.
        labels: Optional array of class labels to include.
        target_names: Optional list of class names for display.
    
    Returns:
        String containing precision, recall, F1-score, and support for each class.
    """
    y_true = np.atleast_1d(y_true)
    y_pred = np.atleast_1d(y_pred)
    
    if labels is None:
        labels = np.unique(np.concatenate([y_true, y_pred]))
    
    if target_names is None:
        target_names = [str(label) for label in labels]
    
    cm = confusion_matrix(y_true, y_pred, labels)
    
    # Calculate metrics for each class
    precision = np.zeros(len(labels))
    recall = np.zeros(len(labels))
    f1 = np.zeros(len(labels))
    support = np.zeros(len(labels), dtype=int)
    
    for i, label in enumerate(labels):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        support[i] = cm[i, :].sum()
        
        precision[i] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall[i] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1[i] = 2 * (precision[i] * recall[i]) / (precision[i] + recall[i]) if (precision[i] + recall[i]) > 0 else 0.0
    
    # Calculate macro and weighted averages
    macro_precision = precision.mean()
    macro_recall = recall.mean()
    macro_f1 = f1.mean()
    
    total_support = support.sum()
    weighted_precision = np.average(precision, weights=support)
    weighted_recall = np.average(recall, weights=support)
    weighted_f1 = np.average(f1, weights=support)
    
    # Format report
    report_lines = ["Classification Report", "=" * 50, ""]
    report_lines.append(f"{'Class':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}")
    report_lines.append("-" * 65)
    
    for i, (label, name) in enumerate(zip(labels, target_names)):
        report_lines.append(
            f"{name:<15} {precision[i]:<12.4f} {recall[i]:<12.4f} "
            f"{f1[i]:<12.4f} {support[i]:<10}"
        )
    
    report_lines.append("-" * 65)
    report_lines.append(
        f"{'Macro Avg':<15} {macro_precision:<12.4f} {macro_recall:<12.4f} "
        f"{macro_f1:<12.4f} {total_support:<10}"
    )
    report_lines.append(
        f"{'Weighted Avg':<15} {weighted_precision:<12.4f} {weighted_recall:<12.4f} "
        f"{weighted_f1:<12.4f} {total_support:<10}"
    )
    
    return "\n".join(report_lines)


def cross_validate(
    estimator,
    X: np.ndarray,
    y: np.ndarray,
    cv: int = 5,
    scoring: str = "accuracy",
    random_state: Optional[int] = None,
    return_train_score: bool = False,
) -> Dict[str, np.ndarray]:
    """
    Perform k-fold cross-validation.
    
    Args:
        estimator: A classifier with fit() and score() methods.
        X: Feature matrix of shape (n_samples, n_features).
        y: Labels of shape (n_samples,).
        cv: Number of cross-validation folds.
        scoring: Scoring metric ("accuracy", "precision", "recall", "f1").
        random_state: Random seed for reproducibility.
        return_train_score: Whether to return training scores.
    
    Returns:
        Dict with keys:
            - 'test_score': Array of test scores for each fold
            - 'train_score': Array of train scores for each fold (if return_train_score=True)
            - 'fit_time': Array of fit times for each fold
            - 'score_time': Array of score times for each fold
    
    Example:
        >>> from oc1 import ObliqueDecisionTree
        >>> tree = ObliqueDecisionTree()
        >>> results = cross_validate(tree, X, y, cv=5)
        >>> print(f"Mean accuracy: {results['test_score'].mean():.3f}")
    """
    X = np.atleast_2d(X)
    y = np.atleast_1d(y)
    
    if len(X) != len(y):
        raise ValueError(f"X has {len(X)} samples but y has {len(y)}")
    
    if cv < 2:
        raise ValueError(f"cv must be >= 2, got {cv}")
    
    rng = np.random.default_rng(random_state)
    n_samples = len(y)
    
    # Create stratified folds
    classes = np.unique(y)
    fold_indices = [[] for _ in range(cv)]
    
    for cls in classes:
        cls_indices = np.where(y == cls)[0]
        rng.shuffle(cls_indices)
        
        # Distribute samples across folds
        for i, idx in enumerate(cls_indices):
            fold_indices[i % cv].append(idx)
    
    # Shuffle each fold
    for fold in fold_indices:
        rng.shuffle(fold)
    
    test_scores = []
    train_scores = []
    fit_times = []
    score_times = []
    
    for fold_idx in range(cv):
        # Create train/test split for this fold
        test_indices = fold_indices[fold_idx]
        train_indices = []
        for i, fold in enumerate(fold_indices):
            if i != fold_idx:
                train_indices.extend(fold)
        
        X_train, X_test = X[train_indices], X[test_indices]
        y_train, y_test = y[train_indices], y[test_indices]
        
        # Fit and time
        start_time = time.time()
        estimator.fit(X_train, y_train)
        fit_time = time.time() - start_time
        fit_times.append(fit_time)
        
        # Score and time
        start_time = time.time()
        test_score = _compute_score(estimator, X_test, y_test, scoring)
        score_time = time.time() - start_time
        score_times.append(score_time)
        test_scores.append(test_score)
        
        if return_train_score:
            train_score = _compute_score(estimator, X_train, y_train, scoring)
            train_scores.append(train_score)
    
    results = {
        'test_score': np.array(test_scores),
        'fit_time': np.array(fit_times),
        'score_time': np.array(score_times),
    }
    
    if return_train_score:
        results['train_score'] = np.array(train_scores)
    
    return results


def _compute_score(estimator, X: np.ndarray, y: np.ndarray, scoring: str) -> float:
    """Compute score using specified metric."""
    if scoring == "accuracy":
        return estimator.score(X, y)
    elif scoring == "precision":
        y_pred = estimator.predict(X)
        cm = confusion_matrix(y, y_pred)
        tp = np.diag(cm).sum()
        fp = (cm.sum(axis=0) - np.diag(cm)).sum()
        return tp / (tp + fp) if (tp + fp) > 0 else 0.0
    elif scoring == "recall":
        y_pred = estimator.predict(X)
        cm = confusion_matrix(y, y_pred)
        tp = np.diag(cm).sum()
        fn = (cm.sum(axis=1) - np.diag(cm)).sum()
        return tp / (tp + fn) if (tp + fn) > 0 else 0.0
    elif scoring == "f1":
        y_pred = estimator.predict(X)
        cm = confusion_matrix(y, y_pred)
        tp = np.diag(cm).sum()
        fp = (cm.sum(axis=0) - np.diag(cm)).sum()
        fn = (cm.sum(axis=1) - np.diag(cm)).sum()
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    else:
        raise ValueError(f"Unknown scoring metric: {scoring}")


__all__ = [
    "cross_validate",
    "train_test_split",
    "confusion_matrix",
    "classification_report",
]
