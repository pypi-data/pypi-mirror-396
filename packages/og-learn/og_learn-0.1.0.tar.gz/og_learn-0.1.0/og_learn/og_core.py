"""
OG Core Components - The heart of Overfit-to-Generalization

This module contains the core OG functions:
- generate_OG_componment: Generate pseudo-labels with density-aware sampling
- initialize_OG_componment: Initialize high-variance model for pseudo-label generation

All HV model parameters are from presets.py (copied from OG_transformer/appendix/represent_analysis.py)
"""

import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import torch


def initialize_OG_componment(X_train, y_train, model_type="lgb"):
    """
    Initialize a high-variance (HV) model for pseudo-label generation.
    
    Parameters
    ----------
    X_train : array-like
        Training features
    y_train : array-like
        Training targets
    model_type : str or model object
        Type of HV model. Options:
        - 'lgb', 'lightgbm': Standard LightGBM
        - 'biglightgbm': Large LightGBM (more leaves)
        - 'xgboost': Standard XGBoost
        - 'bigxgboost': Large XGBoost
        - 'catboost': Standard CatBoost
        - 'bigcatboost': Large CatBoost
        - 'random_forest': Random Forest
        - 'decision_tree': Decision Tree
        - Or a custom model instance with fit/predict interface
    
    Returns
    -------
    model : fitted model
        Fitted HV model for pseudo-label generation
    """
    # If model_type is already a model instance, just fit it
    if not isinstance(model_type, str):
        model = model_type
        model.fit(X_train, y_train)
        return model

    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Original OG_transformer only supports these 3 string options with FIXED params
    # Or you can pass a model instance directly (handled above)
    
    if model_type == "lgb":
        from lightgbm import LGBMRegressor   
        param_grid = {
            "n_estimators": 500,
            'num_leaves': 1200,
            'max_depth': 20,
            'learning_rate': 0.2,
            'min_child_samples': 22,
            'min_child_weight': 0.001,
            'subsample': 0.7,
            'colsample_bytree': 0.9,
        }
        model = LGBMRegressor(random_state=42, verbose=-1, **param_grid)
        
    elif model_type == "xgboost":
        from xgboost import XGBRegressor
        param_grid = {
            'n_estimators': 1200,
            'max_depth': 10, 
            'min_child_weight': 4,
            'subsample': 0.9,
            'colsample_bytree': 0.9,
            'reg_alpha': 0.1, 
            'reg_lambda': 3,
            'learning_rate': 0.1
        }
        model = XGBRegressor(random_state=42, device=device, **param_grid)
        
    elif model_type == "catboost":
        from catboost import CatBoostRegressor
        param_grid = {
            "iterations": 1000,
            "learning_rate": 0.05,
            "depth": 7,
            "l2_leaf_reg": 0.1,
            "border_count": 64,
            "od_wait": 100,
            "task_type": "GPU" if device == "cuda" else "CPU",
            "bootstrap_type": "Bayesian",
            "min_data_in_leaf": 1,
            "grow_policy": "Depthwise",
        }
        model = CatBoostRegressor(random_state=42, verbose=0, **param_grid)
        
    else:
        raise ValueError(f"Unsupported model_type: {model_type}. Use 'lgb', 'xgboost', 'catboost', or pass a model instance.")
    
    model.fit(X_train, y_train)
    return model


def generate_OG_componment(model, X_train, density_col=None, oscillation=0.05, alpha=1.0, label='pseudo_label'):
    """
    Generate training data with OG strategy.
    
    This is called at every epoch to generate new pseudo-labels with:
    1. Density-aware sampling (prioritize sparse regions)
    2. Feature noise injection (oscillation)
    3. Pseudo-label generation from HV model
    
    Parameters
    ----------
    model : fitted model
        HV model for pseudo-label generation
    X_train : pd.DataFrame
        Training features
    density_col : pd.Series, optional
        Density values for each sample (higher = denser area)
    oscillation : float, default=0.05
        Noise level to add to features (fraction of std)
    alpha : float, default=1.0
        Strength of density-based weighting (0=uniform, higher=more sparse-focused)
    label : str, default='pseudo_label'
        Column name for pseudo-labels
    
    Returns
    -------
    X_with_noise : pd.DataFrame
        Sampled features with noise added
    y_pseudo : pd.DataFrame
        Pseudo-labels from HV model
    """
    # 1. Compute density-based weights
    if density_col is not None:
        densities = density_col.values.astype(np.float32)
        
        min_density = densities.min()
        if min_density <= 0:
            densities = densities - min_density + 1e-6  # Ensure all values are positive
        
        weights = 1 / (densities + 1e-6)  # Inverse density (sparse = higher weight)
        weights = weights ** alpha        # Control strength with alpha
        weights = weights / weights.sum()  # Normalize to sum 1
        sample_indices = np.random.choice(len(X_train), size=len(X_train), replace=True, p=weights)
        X_train_sampled = X_train.iloc[sample_indices].copy()
    else: 
        X_train_sampled = X_train.copy()
    
    # 2. Add noise to sampled features
    X_train_with_noise = X_train_sampled.copy()
    for col in X_train_with_noise.columns:
        std = X_train[col].std()
        noise = np.random.normal(0, oscillation * std, size=X_train_with_noise.shape[0])
        X_train_with_noise[col] += noise.astype(np.float32)
    
    # 3. Generate pseudo-labels from the HV model
    hv_preds = model.predict(X_train_with_noise)
    y_pseudo = pd.DataFrame(hv_preds.astype(np.float32), columns=[label])
    
    return X_train_with_noise, y_pseudo
