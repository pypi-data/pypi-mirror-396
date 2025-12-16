# og-learn

**Overfit-to-Generalization Framework for Equitable Spatiotemporal Modeling**

[![PyPI version](https://badge.fury.io/py/og-learn.svg)](https://badge.fury.io/py/og-learn)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

`og-learn` is a Python library that implements the Overfit-to-Generalization (OG) framework, designed to address **local overfitting** in spatiotemporal machine learning models. The framework redistributes predictive capacity from data-rich to data-poor regions through a two-stage approach.

### The Problem: Local Overfitting

Models trained on non-uniformly distributed observations tend to:
- **Overfit** to data-dense regions (achieving high accuracy)
- **Underperform** in sparse areas (poor generalization)
- Show **inconsistent optimal hyperparameters** across different validation groups

This disparity is often invisible when using conventional global metrics.

### The Solution: OG Framework

The OG framework exploits complementary properties of different model architectures:

1. **Stage 1 (Overfit)**: A high-variance model (e.g., LightGBM) is deliberately overfitted to capture local patterns and generate pseudo-labels.

2. **Stage 2 (Generalization)**: A low-variance model (e.g., MLP, Transformer) learns from the pseudo-labels with density-aware sampling and noise injection.

## Installation

```bash
pip install og-learn
```

## Quick Start

```python
from og_learn import OGFramework
from og_learn.models import LightGBMOverfitter, TransformerRegressor

# Initialize the OG framework
og = OGFramework(
    hv_model=LightGBMOverfitter(),  # High-variance model for Stage 1
    lv_model=TransformerRegressor(), # Low-variance model for Stage 2
)

# Fit the model
og.fit(X_train, y_train, coords=coordinates)

# Predict
predictions = og.predict(X_test)
```

## Key Features

- **Density-Aware Sampling**: Prioritizes sparse regions and rare covariate patterns
- **Unlimited Synthetic Target Generation**: Generates high-fidelity pseudo-labels via spatial perturbation
- **Flexible Model Pairing**: Supports various HV/LV model combinations
- **Cross-Validation Strategies**: Built-in time-wise, site-wise, region-wise, and spatiotemporal-wise CV

## Supported Models

### High-Variance (HV) Models
- LightGBM
- XGBoost
- CatBoost

### Low-Variance (LV) Models
- MLP (Multi-Layer Perceptron)
- Transformer Regressor
- ResNet

## Documentation

For full documentation, see [documentation link].

## Citation

If you use this package in your research, please cite:

```bibtex
@article{liang2025og,
  title={Countering Local Overfitting for Equitable Spatiotemporal Modeling},
  author={Liang, Zhehao and Castruccio, Stefano and Crippa, Paola},
  journal={},
  year={2025}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

