# Evaluation Metric Configuration Guide

The MPDistil framework now supports user-controlled evaluation metrics. You can specify which metric to use when initializing your model.

## Available Metrics

### 1. **Accuracy** (Default)
Simple classification accuracy.

```python
model = MPDistil(
    task_name='CB',
    num_labels=3,
    metric='accuracy'  # or omit for default
)
```

### 2. **F1 Score**
Macro F1 score and accuracy (useful for imbalanced datasets).

```python
model = MPDistil(
    task_name='CB',
    num_labels=3,
    metric='f1'
)
```

Returns: `{'acc': ..., 'f1': ..., 'acc_and_f1': ...}`

### 3. **Matthews Correlation Coefficient (MCC)**
For binary classification tasks, especially with class imbalance.

```python
model = MPDistil(
    task_name='CoLA',
    num_labels=2,
    metric='mcc'
)
```

Returns: `{'mcc': ...}`

### 4. **Correlation**
Pearson and Spearman correlation for regression tasks.

```python
model = MPDistil(
    task_name='STS-B',
    task_type='regression',
    metric='correlation'
)
```

Returns: `{'pearson': ..., 'spearmanr': ..., 'corr': ...}`

### 5. **Auto**
Automatically selects metric based on task name.

```python
model = MPDistil(
    task_name='CB',
    num_labels=3,
    metric='auto'  # Will use 'f1' for CB task
)
```

**Auto-detection mapping:**
- `boolq`, `copa`, `rte`, `wic`, `wsc` → accuracy
- `cb` → F1 score
- `sts-b`, `stsb` → correlation
- Default → accuracy

## Complete Example

```python
from mpdistil import MPDistil, load_superglue_dataset

# Load data
loaders, num_labels = load_superglue_dataset('CB')

# Initialize with F1 metric
model = MPDistil(
    task_name='CB',
    num_labels=num_labels,
    metric='f1',  # Use F1 instead of accuracy
    student_layers=6
)

# Train
history = model.train(
    train_loader=loaders['train'],
    val_loader=loaders['val'],
    teacher_epochs=10,
    student_epochs=10
)

# The model will use F1 score for:
# - Phase 1: Teacher evaluation
# - Phase 2: Student evaluation
# - Phase 3: Meta-teacher rewards
# - Phase 4: Curriculum learning rewards
```

## Changing Metric After Initialization

You can also change the metric after creating the model:

```python
model = MPDistil(task_name='CB', num_labels=3)

# Change metric before training
model.metric = 'f1'

history = model.train(...)
```

## Custom Metrics

To add custom metrics, modify `mpdistil/metrics.py`:

1. Add your metric function:
```python
def custom_metric(preds, labels):
    # Your implementation
    return {"custom": score}
```

2. Update `MetricCalculator._metric_fn_map`:
```python
self._metric_fn_map = {
    'accuracy': ...,
    'custom': custom_metric,  # Add your metric
}
```

3. Use it:
```python
model = MPDistil(..., metric='custom')
```

## Metric Output in Training History

The training history will contain metric results:

```python
history = model.train(...)

# Phase 1 (Teacher)
print(history['phase1']['val_metrics'])
# [{'acc': 0.85, 'task': 'cb', 'val_loss': 0.42}, ...]

# Phase 2 (Student)
print(history['phase2']['val_metrics'])
# [{'f1': 0.82, 'acc': 0.84, 'acc_and_f1': 0.83, ...}, ...]
```

## Notes

- The metric is used consistently across all training phases
- For language modeling tasks, perplexity is automatically used
- Changing the metric doesn't affect the loss function (distillation loss)
- The metric is only for evaluation and progress tracking
