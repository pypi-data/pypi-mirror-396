"""
Preset configurations for OG models.

All presets are copied from OG_transformer/appendix/represent_analysis.py
to ensure consistency with the original implementation.

HV (High-Variance) Models: For overfitting / pseudo-label generation
- LightGBM, BigLightGBM, XGBoost, BigXGBoost, CatBoost, BigCatBoost
- RandomForest, DecisionTree

LV (Low-Variance) Models: For generalization
- MLP, BigMLP, ResNet, Transformer, GTransformer
"""

import torch


def get_device():
    """Get best available device."""
    return "cuda" if torch.cuda.is_available() else "cpu"


# =============================================================================
# HV Model Presets (High-Variance for pseudo-label generation)
# From get_model_configs() in represent_analysis.py
# =============================================================================

HV_PRESETS = {
    'lightgbm': {
        'class': 'LGBMRegressor',
        'module': 'lightgbm',
        'params': {
            'n_estimators': 100,
            'num_leaves': 300,
            'max_depth': 20,
            'learning_rate': 0.2,
            'min_child_samples': 22,
            'min_child_weight': 0.001,
            'subsample': 0.7,
            'colsample_bytree': 0.9,
            'random_state': 42,
            'verbose': -1
        }
    },
    'biglightgbm': {
        'class': 'LGBMRegressor',
        'module': 'lightgbm',
        'params': {
            'n_estimators': 500,  # Original OG uses 500
            'num_leaves': 1200,
            'max_depth': 20,
            'learning_rate': 0.2,
            'min_child_samples': 22,
            'min_child_weight': 0.001,
            'subsample': 0.7,
            'colsample_bytree': 0.9,
            'random_state': 42,
            'verbose': -1
        }
    },
    'xgboost': {
        'class': 'XGBRegressor',
        'module': 'xgboost',
        'params': {
            'n_estimators': 100,
            'max_depth': 16,
            'min_child_weight': 4,
            'subsample': 0.9,
            'colsample_bytree': 0.9,
            'reg_alpha': 0.1,
            'reg_lambda': 3,
            'learning_rate': 0.175,
            'random_state': 42
        }
    },
    'bigxgboost': {
        'class': 'XGBRegressor',
        'module': 'xgboost',
        'params': {
            'n_estimators': 1200,
            'max_depth': 10,
            'min_child_weight': 4,
            'subsample': 0.9,
            'colsample_bytree': 0.9,
            'reg_alpha': 0.1,
            'reg_lambda': 3,
            'learning_rate': 0.175,
            'random_state': 42
        }
    },
    'catboost': {
        'class': 'CatBoostRegressor',
        'module': 'catboost',
        'params': {
            'iterations': 700,
            'depth': 6,
            'learning_rate': 0.1,
            'l2_leaf_reg': 2,
            'border_count': 64,
            'od_wait': 100,
            'task_type': "GPU",
            'bootstrap_type': "Bayesian",
            'min_data_in_leaf': 1,
            'grow_policy': "Depthwise",
            'random_state': 42,
            'verbose': 0
        }
    },
    'bigcatboost': {
        'class': 'CatBoostRegressor',
        'module': 'catboost',
        'params': {
            'iterations': 1000,
            'depth': 7,
            'learning_rate': 0.1,
            'l2_leaf_reg': 2,
            'border_count': 64,
            'od_wait': 100,
            'task_type': "GPU",
            'bootstrap_type': "Bayesian",
            'min_data_in_leaf': 1,
            'grow_policy': "Depthwise",
            'random_state': 42,
            'verbose': 0
        }
    },
    'random_forest': {
        'class': 'RandomForestRegressor',
        'module': 'sklearn.ensemble',
        'params': {
            'max_depth': 20,
            'n_estimators': 5,
            'min_samples_leaf': 2,
            'max_features': 0.8,
            'bootstrap': True,
            'max_samples': 0.9,
            'n_jobs': -1,
            'random_state': 42,
            'verbose': 0
        }
    },
    'decision_tree': {
        'class': 'DecisionTreeRegressor',
        'module': 'sklearn.tree',
        'params': {
            'max_depth': 25,
            'min_samples_split': 2,
            'random_state': 42
        }
    },
    'linear_regression': {
        'class': 'Ridge',
        'module': 'sklearn.linear_model',
        'params': {
            'alpha': 1.0,
            'fit_intercept': True,
            'random_state': 42
        }
    }
}


# =============================================================================
# LV Model Presets (Low-Variance for generalization)
# From get_model_configs() in represent_analysis.py
# =============================================================================

LV_PRESETS = {
    'mlp': {
        'class': 'MLPRegressor',
        'module': 'og_learn.models.mlp',
        'params': {
            'hidden_dims': [512, 256, 128],
            'dropout': 0.1,
            'activation': 'relu',
            'lr': 1e-3,
            'batch_size': 1024
            # epochs and num_features set dynamically
        }
    },
    'bigmlp': {
        'class': 'MLPRegressor',
        'module': 'og_learn.models.mlp',
        'params': {
            'hidden_dims': [1024, 512, 512, 512, 512, 512, 512, 256, 256, 256, 256, 256, 128, 64],
            'dropout': 0.1,
            'activation': 'relu',
            'lr': 1e-3,
            'batch_size': 1024
        }
    },
    'resnet': {
        'class': 'ResNetRegressor',
        'module': 'og_learn.models.resnet',
        'params': {
            'hidden_dim': 512,
            'num_blocks': 6,
            'dropout': 0.1,
            'activation': 'relu',  # From resnet_config
            'lr': 1e-3,
            'batch_size': 1024
        }
    },
    'transformer': {
        'class': 'FTTransformerRegressor',
        'module': 'og_learn.models.transformer',
        'params': {
            'emb_dim': 32,
            'depth': 6,
            'dropout': 0.05,
            'global_feature': False,
            'local_feature': True,
            'pooling': False
        }
    },
}


# Early stopping variants (with early_stopping=True during training)
LV_EARLY_PRESETS = {
    'mlp_early': LV_PRESETS['mlp'].copy(),
    'resnet_early': LV_PRESETS['resnet'].copy(),
    'transformer_early': LV_PRESETS['transformer'].copy()
}


def get_hv_model(name, **override_params):
    """
    Get a high-variance model instance.
    
    Parameters
    ----------
    name : str
        Model name: 'lightgbm', 'biglightgbm', 'xgboost', 'bigxgboost', 
                    'catboost', 'bigcatboost', 'random_forest', 'decision_tree',
                    'linear_regression'
    **override_params : dict
        Parameters to override defaults
    
    Returns
    -------
    model : estimator
        Unfitted model instance
    """
    if name not in HV_PRESETS:
        raise ValueError(f"Unknown HV preset: {name}. Available: {list(HV_PRESETS.keys())}")
    
    config = HV_PRESETS[name]
    params = config['params'].copy()
    params.update(override_params)
    
    # Handle device for XGBoost
    if name in ['xgboost', 'bigxgboost']:
        device = get_device()
        if device == "cuda":
            params['device'] = device
    
    # Handle task_type for CatBoost
    if name in ['catboost', 'bigcatboost']:
        params['task_type'] = "GPU" if get_device() == "cuda" else "CPU"
    
    # Import and create model
    if name in ['lightgbm', 'biglightgbm']:
        from lightgbm import LGBMRegressor
        return LGBMRegressor(**params)
    elif name in ['xgboost', 'bigxgboost']:
        from xgboost import XGBRegressor
        return XGBRegressor(**params)
    elif name in ['catboost', 'bigcatboost']:
        from catboost import CatBoostRegressor
        return CatBoostRegressor(**params)
    elif name == 'random_forest':
        from sklearn.ensemble import RandomForestRegressor
        return RandomForestRegressor(**params)
    elif name == 'decision_tree':
        from sklearn.tree import DecisionTreeRegressor
        return DecisionTreeRegressor(**params)
    elif name == 'linear_regression':
        from sklearn.linear_model import Ridge
        return Ridge(**params)


def get_lv_model(name, num_features, epochs=60, **override_params):
    """
    Get a low-variance model instance.
    
    Parameters
    ----------
    name : str
        Model name: 'mlp', 'bigmlp', 'resnet', 'transformer', 'gtransformer'
                    Also supports '_early' variants for early stopping
    num_features : int
        Number of input features
    epochs : int
        Number of training epochs (default: 60, matching original)
    **override_params : dict
        Parameters to override defaults
    
    Returns
    -------
    model : estimator
        Unfitted model instance
    """
    # Handle early stopping variants
    base_name = name.replace('_early', '')
    
    if base_name not in LV_PRESETS:
        raise ValueError(f"Unknown LV preset: {name}. Available: {list(LV_PRESETS.keys())}")
    
    config = LV_PRESETS[base_name]
    params = config['params'].copy()
    params['num_features'] = num_features
    params['epochs'] = epochs
    params.update(override_params)
    
    # Import and create model
    if base_name in ['mlp', 'bigmlp']:
        from .models.mlp import MLPRegressor
        return MLPRegressor(**params)
    elif base_name == 'resnet':
        from .models.resnet import ResNetRegressor
        return ResNetRegressor(**params)
    elif base_name == 'transformer':
        from .models.transformer import FTTransformerRegressor
        return FTTransformerRegressor(**params)


def list_presets():
    """List all available presets."""
    print("=" * 60)
    print("HV Models (High-Variance for pseudo-label generation):")
    print("-" * 60)
    for name in HV_PRESETS:
        print(f"  - {name}")
    
    print("\n" + "=" * 60)
    print("LV Models (Low-Variance for generalization):")
    print("-" * 60)
    for name in LV_PRESETS:
        print(f"  - {name}")
        print(f"    Also: {name}_early (with early stopping)")
    print("=" * 60)
