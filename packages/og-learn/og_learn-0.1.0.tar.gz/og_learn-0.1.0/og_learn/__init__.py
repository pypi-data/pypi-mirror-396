"""
og-learn: Overfit-to-Generalization Framework for Equitable Spatiotemporal Modeling

This package implements the OG framework for addressing local overfitting
in spatiotemporal machine learning models.

Key Components:
- OGModel: Main class for OG training
- calculate_density: Calculate spatial density
- split_test_train: Data splitting utilities
- simple_feature_engineering: Feature engineering pipeline
"""

__version__ = "0.1.0"
__author__ = "Zhehao Liang"
__email__ = "zliang7@nd.edu"

# Core OG framework
from .framework import OGModel, compare_models, launch_tensorboard

# Data utilities
from .density import calculate_density
from .split import split_test_train
from .feature import simple_feature_engineering
from .utils import load_data, sanity_check, save_split_indices, load_split_indices

# OG core functions (for advanced users)
from .og_core import generate_OG_componment, initialize_OG_componment

# Presets
from .presets import get_hv_model, get_lv_model, HV_PRESETS, LV_PRESETS, list_presets

__all__ = [
    # Main classes
    'OGModel',
    'compare_models',
    'launch_tensorboard',
    
    # Data utilities
    'calculate_density',
    'split_test_train',
    'simple_feature_engineering',
    'load_data',
    'sanity_check',
    'save_split_indices',
    'load_split_indices',
    
    # OG core
    'generate_OG_componment',
    'initialize_OG_componment',
    
    # Presets
    'get_hv_model',
    'get_lv_model',
    'HV_PRESETS',
    'LV_PRESETS',
    'list_presets',
]
