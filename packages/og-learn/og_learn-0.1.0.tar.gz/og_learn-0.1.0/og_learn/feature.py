"""
Feature Engineering utilities for geospatial data.

You can replace these with your own feature engineering methods!
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from tqdm.auto import tqdm


def compute_spatial_harmonics(df):
    """
    Add spatial harmonic features (S1, S2, S3) from longitude/latitude.
    
    These capture global spatial patterns using spherical harmonics.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'longitude' and 'latitude' columns
    
    Returns
    -------
    df : pd.DataFrame
        DataFrame with S1, S2, S3 columns added
    """
    df = df.copy()
    df['S1'] = np.sin(2 * np.pi * df['longitude'] / 360)
    df['S2'] = np.cos(2 * np.pi * df['longitude'] / 360) * np.sin(2 * np.pi * df['latitude'] / 180)
    df['S3'] = np.cos(2 * np.pi * df['longitude'] / 360) * np.cos(2 * np.pi * df['latitude'] / 180)
    return df


def compute_temporal_harmonics(df):
    """
    Add temporal harmonic features (T1, T2, T3) from time column.
    
    These capture seasonal patterns using Fourier features.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'time' column (datetime)
    
    Returns
    -------
    df : pd.DataFrame
        DataFrame with T1, T2, T3, month, hour columns added
    """
    df = df.copy()
    time = pd.to_datetime(df['time'])
    
    # Day of year for seasonal patterns
    doy = time.dt.dayofyear
    N = 365.25
    
    df['T1'] = doy / N  # Linear trend
    df['T2'] = np.cos(2 * np.pi * doy / N)  # Cosine (annual cycle)
    df['T3'] = np.sin(2 * np.pi * doy / N)  # Sine (annual cycle)
    
    # Additional time features
    df['month'] = time.dt.month
    df['hour'] = time.dt.hour
    
    return df


def simple_feature_engineering(df, feature_cols, target_col, 
                                add_spatial_harmonics=True,
                                add_temporal_harmonics=True,
                                standardize=True,
                                verbose=True):
    """
    Simple feature engineering pipeline for geospatial data.
    
    **You can replace this with your own feature engineering method!**
    
    Pipeline steps:
    1. Fill missing values with median
    2. Add temporal harmonics (T1, T2, T3, month, hour) if time column exists
    3. Add spatial harmonics (S1, S2, S3) from lon/lat
    4. Standardize features (zero mean, unit variance)
    
    Behavior:
    - If add_temporal_harmonics=True and 'time' in df: creates T1,T2,T3,month,hour
    - If add_temporal_harmonics=False and 'time' in feature_cols: ERROR (datetime not numeric)
    - If add_spatial_harmonics=True and lon/lat in feature_cols: creates S1,S2,S3, removes lon/lat
    - If add_spatial_harmonics=False and lon/lat in feature_cols: keeps lon/lat as regular features
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    feature_cols : list
        List of feature column names
    target_col : str
        Name of target column
    add_spatial_harmonics : bool, default=True
        Whether to add spatial harmonic features (requires longitude/latitude in df)
    add_temporal_harmonics : bool, default=True
        Whether to add temporal harmonic features (requires time in df)
    standardize : bool, default=True
        Whether to standardize features
    verbose : bool, default=True
        Whether to print progress
    
    Returns
    -------
    X : pd.DataFrame
        Processed feature matrix
    y : pd.Series
        Target values
    feature_names : list
        Final feature column names
    
    Example
    -------
    >>> X, y, features = simple_feature_engineering(
    ...     df, 
    ...     feature_cols=['temperature', 'humidity', 'longitude', 'latitude'],
    ...     target_col='o3'
    ... )
    >>> print(f"Features: {features}")
    """
    df = df.copy()
    feature_cols = list(feature_cols)  # Make a copy
    
    # Validate: 'time' in feature_cols but add_temporal_harmonics=False
    if 'time' in feature_cols and not add_temporal_harmonics:
        raise ValueError(
            "'time' is in feature_cols but add_temporal_harmonics=False. "
            "Either set add_temporal_harmonics=True or remove 'time' from feature_cols "
            "(datetime format cannot be used as a numeric feature)."
        )
    
    # Build pipeline steps for display
    steps = []
    if add_temporal_harmonics and 'time' in df.columns:
        steps.append("temporal harmonics")
    if add_spatial_harmonics and 'longitude' in df.columns:
        steps.append("spatial harmonics")
    if standardize:
        steps.append("standardize")
    
    if verbose:
        print(f"Feature Engineering Pipeline: {' → '.join(['fill NA'] + steps)}")
    
    # Step 1: Select features (excluding 'time' which will be handled separately)
    cols_to_use = [c for c in feature_cols if c != 'time']
    X = df[cols_to_use].copy()
    y = df[target_col].copy()
    
    # Fill missing values with median (only for numeric columns)
    numeric_cols = X.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if X[col].isna().any():
            X[col] = X[col].fillna(X[col].median())
    
    # Step 2: Temporal harmonics (matching original general_feature_engineering)
    if add_temporal_harmonics and 'time' in df.columns:
        time = pd.to_datetime(df['time'])
        doy = time.dt.dayofyear
        N = 365.25
        
        # DatetimeFeatures: month, day_of_month, hour
        X['time_month'] = time.dt.month.astype(np.float32)
        X['time_day_of_month'] = time.dt.day.astype(np.float32)
        X['time_hour'] = time.dt.hour.astype(np.float32)
        
        # Temporal harmonics: T1, T2, T3
        X['T1'] = (doy / N).astype(np.float32)
        X['T2'] = np.cos(2 * np.pi * doy / N).astype(np.float32)
        X['T3'] = np.sin(2 * np.pi * doy / N).astype(np.float32)
        
        if verbose:
            print("  ✓ Added temporal features: time_month, time_day_of_month, time_hour, T1, T2, T3")
    
    # Step 3: Standardize BEFORE spatial harmonics (matching original)
    # Note: Original general_feature_engineering applies StandardScaler before spatial harmonics
    has_lonlat_in_features = 'longitude' in cols_to_use and 'latitude' in cols_to_use
    has_lonlat_in_df = 'longitude' in df.columns and 'latitude' in df.columns
    
    if standardize:
        # Ensure all columns are numeric before standardization
        X = X.astype(np.float32)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
        
        if verbose:
            print("  ✓ Standardized all features")
    
    # Step 4: Spatial harmonics (AFTER standardization, matching original)
    if add_spatial_harmonics and has_lonlat_in_df:
        # Use df's lon/lat (not standardized) for computing harmonics
        if has_lonlat_in_features:
            # Get original lon/lat from df (before standardization)
            lon = df.loc[X.index, 'longitude'].values
            lat = df.loc[X.index, 'latitude'].values
            # Drop standardized lon/lat from X (will be replaced by S1, S2, S3)
            X = X.drop(columns=['longitude', 'latitude'])
        else:
            lon = df['longitude'].values
            lat = df['latitude'].values
        
        X['S1'] = np.sin(2 * np.pi * lon / 360).astype(np.float32)
        X['S2'] = (np.cos(2 * np.pi * lon / 360) * np.sin(2 * np.pi * lat / 180)).astype(np.float32)
        X['S3'] = (np.cos(2 * np.pi * lon / 360) * np.cos(2 * np.pi * lat / 180)).astype(np.float32)
        
        if verbose:
            if has_lonlat_in_features:
                print("  ✓ Added spatial harmonics: S1, S2, S3 (replaced lon/lat)")
            else:
                print("  ✓ Added spatial harmonics: S1, S2, S3")
    elif not add_spatial_harmonics and has_lonlat_in_features:
        # Keep lon/lat as regular features (already standardized if standardize=True)
        if verbose:
            print("  ✓ Keeping longitude/latitude as regular features")
    
    feature_names = list(X.columns)
    
    if verbose:
        print(f"\nFinal features ({len(feature_names)}): {feature_names[:5]}{'...' if len(feature_names) > 5 else ''}")
    
    return X, y, feature_names

