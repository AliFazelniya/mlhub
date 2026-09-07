# Utility Module

This folder contains reusable plotting utilities to support visualization across the repository.

## Contents

- `plot_utils.py` - Utility functions for plotting distributions, correlations, confusion matrices, and ROC curves.

## Summary

The utilities in this folder are intended to:

- Standardize visualization of numeric feature distributions
- Provide clear correlation heatmaps for exploratory analysis
- Render confusion matrices with optional normalization and performance metrics
- Plot ROC curves for binary classification models

## Usage Example

```python
from utility.plot_utils import (
    distribution_plot,
    corr_plot,
    plot_confusion_matrix,
    plot_roc_curve,
)
```

Use these functions inside notebooks to keep visualizations consistent and easy to interpret.
