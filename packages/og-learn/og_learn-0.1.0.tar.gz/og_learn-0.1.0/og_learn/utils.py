"""
Utility functions for og-learn.
"""

import os
import numpy as np
import pandas as pd
from typing import List, Optional, Tuple


def load_data(
    path: str,
    feature_cols: Optional[List[str]] = None,
    target_col: Optional[str] = None,
    verbose: bool = True
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Load and preprocess spatiotemporal data.
    
    Parameters
    ----------
    path : str
        Path to pickle file
    feature_cols : list of str, optional
        List of feature column names to validate
    target_col : str, optional
        Target column name to validate
    verbose : bool, default=True
        Whether to print summary
    
    Returns
    -------
    df : pd.DataFrame
        Loaded and preprocessed DataFrame
    available_features : list of str
        List of available feature columns
    
    Example
    -------
    >>> df, features = load_data('data/df_example.pkl', FEATURE_COLS, TARGET_COL)
    """
    # Load data
    try:
        df = pd.read_pickle(path)
    except Exception as e:
        raise FileNotFoundError(f"Cannot load data from {path}: {e}")
    
    # Convert time column if exists
    if 'time' in df.columns:
        try:
            df['time'] = pd.to_datetime(df['time'])
        except Exception:
            pass  # Keep original if conversion fails
    
    # Convert float64 to float32 for memory efficiency
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].astype('float32')
    
    # Validate feature columns
    available_features = []
    if feature_cols is not None:
        available_features = [c for c in feature_cols if c in df.columns]
        missing = set(feature_cols) - set(available_features)
        if missing and verbose:
            print(f"⚠️ Missing features: {missing}")
    
    # Validate target column
    if target_col is not None and target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in data")
    
    # Print summary
    if verbose:
        n_locations = df.groupby(['longitude', 'latitude']).ngroup().nunique() if 'longitude' in df.columns else 0
        print(f"✓ Loaded {len(df):,} samples from {n_locations:,} locations")
        if 'time' in df.columns:
            print(f"  Time range: {df['time'].min()} to {df['time'].max()}")
        if target_col:
            print(f"  Target: {target_col}")
        if available_features:
            print(f"  Features: {len(available_features)} columns")
    
    return df, available_features


def sanity_check(
    df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str,
    verbose: bool = True
) -> bool:
    """
    Perform sanity checks on the data.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    feature_cols : list of str
        Feature column names
    target_col : str
        Target column name
    verbose : bool, default=True
        Whether to print results
    
    Returns
    -------
    passed : bool
        True if all checks pass
    """
    issues = []
    
    # Check required columns
    required = ['longitude', 'latitude']
    for col in required:
        if col not in df.columns:
            issues.append(f"Missing required column: {col}")
    
    # Check target
    if target_col not in df.columns:
        issues.append(f"Target column '{target_col}' not found")
    
    # Check features
    missing_features = [c for c in feature_cols if c not in df.columns]
    if missing_features:
        issues.append(f"Missing features: {missing_features}")
    
    # Check for NaN in target
    if target_col in df.columns:
        nan_count = df[target_col].isna().sum()
        if nan_count > 0:
            issues.append(f"Target has {nan_count} NaN values")
    
    # Print results
    if verbose:
        if issues:
            print("❌ Sanity check failed:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✓ Sanity check passed")
        
        # Check feature engineering conditions
        print("\nFeature engineering options:")
        
        # Temporal harmonics
        has_time = 'time' in df.columns
        if has_time:
            print("  ✓ Temporal harmonics available (time column found)")
        else:
            print("  ✗ Temporal harmonics NOT available (no time column)")
        
        # Spatial harmonics
        has_lonlat = 'longitude' in df.columns and 'latitude' in df.columns
        if has_lonlat:
            print("  ✓ Spatial harmonics available (longitude/latitude found)")
        else:
            print("  ✗ Spatial harmonics NOT available (missing longitude/latitude)")
    
    return len(issues) == 0


def save_split_indices(
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    save_dir: str = 'diagnostics',
    prefix: str = 'split'
) -> dict:
    """
    Save train/test split indices to files.
    
    Parameters
    ----------
    train_idx : array-like
        Training indices
    test_idx : array-like
        Test indices
    save_dir : str, default='diagnostics'
        Directory to save files
    prefix : str, default='split'
        Filename prefix
    
    Returns
    -------
    paths : dict
        Dictionary with 'train' and 'test' file paths
    """
    os.makedirs(save_dir, exist_ok=True)
    
    train_path = os.path.join(save_dir, f'{prefix}_train_idx.npy')
    test_path = os.path.join(save_dir, f'{prefix}_test_idx.npy')
    
    np.save(train_path, train_idx)
    np.save(test_path, test_idx)
    
    print(f"✓ Split indices saved to {save_dir}/")
    print(f"  - {prefix}_train_idx.npy ({len(train_idx):,} samples)")
    print(f"  - {prefix}_test_idx.npy ({len(test_idx):,} samples)")
    
    return {'train': train_path, 'test': test_path}


def load_split_indices(
    save_dir: str = 'diagnostics',
    prefix: str = 'split'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load train/test split indices from files.
    
    Parameters
    ----------
    save_dir : str, default='diagnostics'
        Directory where files are saved
    prefix : str, default='split'
        Filename prefix
    
    Returns
    -------
    train_idx : np.ndarray
        Training indices
    test_idx : np.ndarray
        Test indices
    """
    train_path = os.path.join(save_dir, f'{prefix}_train_idx.npy')
    test_path = os.path.join(save_dir, f'{prefix}_test_idx.npy')
    
    train_idx = np.load(train_path)
    test_idx = np.load(test_path)
    
    print(f"✓ Loaded split indices from {save_dir}/")
    print(f"  - Train: {len(train_idx):,} samples")
    print(f"  - Test: {len(test_idx):,} samples")
    
    return train_idx, test_idx

