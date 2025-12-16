"""Evaluation metrics for MPDistil.

This module provides metric computation functions using HuggingFace evaluate library.
Supports SuperGLUE metrics and standard classification/regression metrics.
"""

from typing import Dict, List, Union, Optional
import numpy as np
import torch

try:
    import evaluate
except ImportError:
    raise ImportError(
        "The 'evaluate' library is required for metrics. "
        "Install it with: pip install evaluate"
    )


def compute_perplexity(loss: float) -> float:
    """Compute perplexity from loss.
    
    Args:
        loss: Cross-entropy loss value
        
    Returns:
        Perplexity score
    """
    return np.exp(loss)


def compute_perplexity_from_logits(
    logits: torch.Tensor,
    labels: torch.Tensor,
    ignore_index: int = -100
) -> float:
    """Compute perplexity from logits and labels.
    
    Args:
        logits: Model logits [batch_size, seq_len, vocab_size]
        labels: Ground truth labels [batch_size, seq_len]
        ignore_index: Index to ignore in loss computation (default: -100)
        
    Returns:
        Perplexity score
    """
    import torch.nn.functional as F
    
    # Flatten logits and labels
    logits_flat = logits.view(-1, logits.size(-1))
    labels_flat = labels.view(-1)
    
    # Compute cross-entropy loss
    loss = F.cross_entropy(logits_flat, labels_flat, ignore_index=ignore_index)
    
    # Convert to perplexity
    return compute_perplexity(loss.item())


def simple_accuracy(preds: Union[List, np.ndarray], labels: Union[List, np.ndarray]) -> float:
    """Compute accuracy using HuggingFace evaluate.
    
    Args:
        preds: Predictions
        labels: Ground truth labels
        
    Returns:
        Accuracy score
    """
    metric = evaluate.load("accuracy")
    result = metric.compute(predictions=preds, references=labels)
    return result["accuracy"]


def acc_and_f1(preds: Union[List, np.ndarray], labels: Union[List, np.ndarray]) -> Dict[str, float]:
    """Compute accuracy and macro F1 score using HuggingFace evaluate.
    
    Used for tasks like CB that require both metrics.
    
    Args:
        preds: Predictions
        labels: Ground truth labels
        
    Returns:
        Dict with 'acc', 'f1', and 'acc_and_f1' (average)
    """
    acc_metric = evaluate.load("accuracy")
    f1_metric = evaluate.load("f1")
    
    acc = acc_metric.compute(predictions=preds, references=labels)["accuracy"]
    f1 = f1_metric.compute(predictions=preds, references=labels, average="macro")["f1"]
    
    return {
        "acc": acc,
        "f1": f1,
        "acc_and_f1": (acc + f1) / 2,
    }


def pearson_and_spearman(preds: Union[List, np.ndarray], labels: Union[List, np.ndarray]) -> Dict[str, float]:
    """Compute Pearson and Spearman correlation using HuggingFace evaluate.
    
    Used for regression tasks like STS-B.
    
    Args:
        preds: Predictions
        labels: Ground truth labels
        
    Returns:
        Dict with 'pearson', 'spearmanr', and 'corr' (average)
    """
    pearson_metric = evaluate.load("pearsonr")
    spearman_metric = evaluate.load("spearmanr")
    
    pearson_corr = pearson_metric.compute(predictions=preds, references=labels)["pearsonr"]
    spearman_corr = spearman_metric.compute(predictions=preds, references=labels)["spearmanr"]
    
    return {
        "pearson": pearson_corr,
        "spearmanr": spearman_corr,
        "corr": (pearson_corr + spearman_corr) / 2,
    }


def matthews_correlation(preds: Union[List, np.ndarray], labels: Union[List, np.ndarray]) -> Dict[str, float]:
    """Compute Matthews Correlation Coefficient using HuggingFace evaluate.
    
    Args:
        preds: Predictions
        labels: Ground truth labels
        
    Returns:
        Dict with 'mcc'
    """
    metric = evaluate.load("matthews_correlation")
    result = metric.compute(predictions=preds, references=labels)
    return {"mcc": result["matthews_correlation"]}


def compute_metrics(
    task_name: str,
    preds: Union[List, np.ndarray],
    labels: Union[List, np.ndarray],
    metric_name: str = 'auto'
) -> Dict[str, float]:
    """Compute task-specific metrics using HuggingFace evaluate.
    
    Args:
        task_name: Name of task (lowercase)
        preds: Predictions
        labels: Ground truth labels
        metric_name: Metric to compute ('auto', 'accuracy', 'f1', 'mcc', 'correlation')
        
    Returns:
        Dict with computed metrics
    """
    assert len(preds) == len(labels), "Predictions and labels must have same length"
    
    if metric_name == 'auto':
        # Auto-detect based on task name
        if task_name in ["boolq", "copa", "rte", "wic", "wsc"]:
            return {"acc": simple_accuracy(preds, labels)}
        elif task_name == "cb":
            return acc_and_f1(preds, labels)
        elif task_name in ["sts-b", "stsb"]:
            return pearson_and_spearman(preds, labels)
        else:
            # Default to accuracy
            return {"acc": simple_accuracy(preds, labels)}
    elif metric_name == 'accuracy':
        return {"acc": simple_accuracy(preds, labels)}
    elif metric_name == 'f1':
        return acc_and_f1(preds, labels)
    elif metric_name == 'mcc':
        return matthews_correlation(preds, labels)
    elif metric_name == 'correlation':
        return pearson_and_spearman(preds, labels)
    else:
        raise ValueError(f"Unknown metric: {metric_name}")


class MetricCalculator:
    """Handles metric computation with configurable metric type using HuggingFace evaluate.
    
    This class provides a unified interface for computing various metrics using the
    HuggingFace evaluate library, which ensures compatibility with standard benchmarks
    and SuperGLUE evaluation protocols.
    
    Args:
        metric_name: Name of metric ('accuracy', 'f1', 'mcc', 'correlation')
    
    Supported Metrics:
        - accuracy: Standard classification accuracy using 'accuracy' metric
        - f1: Macro F1 score and accuracy using 'f1' and 'accuracy' metrics
        - mcc: Matthews Correlation Coefficient using 'matthews_correlation' metric
        - correlation: Pearson and Spearman correlation using 'pearsonr' and 'spearmanr' metrics
    """
    
    def __init__(self, metric_name: str = 'accuracy'):
        self.metric_name = metric_name
        
        self._metric_fn_map = {
            'accuracy': lambda p, l: {"acc": simple_accuracy(p, l)},
            'f1': acc_and_f1,
            'mcc': matthews_correlation,
            'correlation': pearson_and_spearman,
        }
        
        if metric_name not in self._metric_fn_map:
            raise ValueError(
                f"Unknown metric: {metric_name}. "
                f"Supported metrics: {list(self._metric_fn_map.keys())}"
            )
    
    def compute(self, preds: Union[List, np.ndarray], labels: Union[List, np.ndarray]) -> Dict[str, float]:
        """Compute the configured metric using HuggingFace evaluate.
        
        Args:
            preds: Predictions
            labels: Ground truth labels
            
        Returns:
            Dict with computed metrics
        """
        return self._metric_fn_map[self.metric_name](preds, labels)
    
    def get_best_score(self, metrics: Dict[str, float]) -> float:
        """Extract the main score from metrics dict.
        
        Args:
            metrics: Dict of computed metrics
            
        Returns:
            The primary metric value for comparison
        """
        if 'mcc' in metrics:
            return metrics['mcc']
        elif 'f1' in metrics:
            return metrics['f1']
        elif 'acc' in metrics:
            return metrics['acc']
        elif 'spearmanr' in metrics:
            return metrics['spearmanr']
        elif 'corr' in metrics:
            return metrics['corr']
        else:
            # Return first value
            return list(metrics.values())[0]
